from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid
import os

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models import User
from app.schemas import OCRResponse, QuizGenerationResponse
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
ocr_service = OCRService()
llm_service = LLMService()
storage_service = StorageService()

@router.post("/extract-text", response_model=OCRResponse)
@limiter.limit(settings.RATE_LIMIT_OCR)
async def extract_text_from_image(
    request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Extract text from uploaded image using OCR"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are supported"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    try:
        # Process OCR
        ocr_result = await ocr_service.extract_text_from_image(file_content)
        
        return OCRResponse(
            text=ocr_result["text"],
            confidence=ocr_result["confidence"],
            processing_time=ocr_result["processing_time"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )

@router.post("/generate-quiz", response_model=QuizGenerationResponse)
@limiter.limit(settings.RATE_LIMIT_OCR)
async def generate_quiz_from_text(
    request,
    text: str,
    num_questions: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate quiz questions from text using AI"""
    
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    if num_questions < 1 or num_questions > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of questions must be between 1 and 10"
        )
    
    try:
        # Generate quiz using LLM
        quiz_result = await llm_service.generate_quiz_from_text(text, num_questions)
        
        return QuizGenerationResponse(
            questions=quiz_result["questions"],
            total_questions=len(quiz_result["questions"]),
            generation_time=quiz_result["generation_time"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation failed: {str(e)}"
        )

@router.post("/process-image-to-quiz", response_model=QuizGenerationResponse)
@limiter.limit(settings.RATE_LIMIT_OCR)
async def process_image_to_quiz(
    request,
    file: UploadFile = File(...),
    num_questions: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Complete pipeline: OCR + Quiz generation from image"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are supported"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    if num_questions < 1 or num_questions > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of questions must be between 1 and 10"
        )
    
    try:
        # Step 1: Extract text using OCR
        ocr_result = await ocr_service.extract_text_from_image(file_content)
        
        if not ocr_result["text"].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from the image"
            )
        
        # Step 2: Generate quiz from extracted text
        quiz_result = await llm_service.generate_quiz_from_text(
            ocr_result["text"], 
            num_questions
        )
        
        return QuizGenerationResponse(
            questions=quiz_result["questions"],
            total_questions=len(quiz_result["questions"]),
            generation_time=quiz_result["generation_time"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )