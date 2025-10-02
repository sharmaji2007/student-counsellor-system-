from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, get_teacher_user
from app.models import User, Assignment, Submission
from app.schemas import (
    Assignment as AssignmentSchema,
    AssignmentCreate,
    Submission as SubmissionSchema,
    FileUploadResponse
)
from app.services.storage_service import StorageService
from app.services.ocr_service import OCRService
from app.core.config import settings

router = APIRouter()
storage_service = StorageService()
ocr_service = OCRService()

@router.get("/", response_model=List[AssignmentSchema])
async def get_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get assignments for current user"""
    if current_user.role.value == "student":
        # Students see assignments for their class
        # For now, get all assignments (in real app, filter by student's class)
        result = await db.execute(select(Assignment))
    else:
        # Teachers see assignments they created
        result = await db.execute(
            select(Assignment).where(Assignment.teacher_id == current_user.id)
        )
    
    assignments = result.scalars().all()
    return assignments

@router.post("/", response_model=AssignmentSchema)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Create new assignment (teachers only)"""
    db_assignment = Assignment(
        **assignment_data.dict(),
        teacher_id=current_user.id
    )
    
    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)
    
    return db_assignment

@router.get("/{assignment_id}", response_model=AssignmentSchema)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific assignment"""
    result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment

@router.get("/{assignment_id}/submissions", response_model=List[SubmissionSchema])
async def get_assignment_submissions(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get all submissions for an assignment (teachers only)"""
    # Verify assignment exists and user has access
    assignment_result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = assignment_result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Get submissions
    result = await db.execute(
        select(Submission).where(Submission.assignment_id == assignment_id)
    )
    submissions = result.scalars().all()
    
    return submissions

@router.post("/{assignment_id}/submit", response_model=SubmissionSchema)
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit assignment with file upload"""
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit assignments"
        )
    
    # Verify assignment exists
    assignment_result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = assignment_result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if already submitted
    existing_result = await db.execute(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment already submitted"
        )
    
    # Validate file
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Upload file to storage
    file_path = await storage_service.upload_file(
        file_content, 
        unique_filename,
        content_type=file.content_type
    )
    
    # Create submission record
    db_submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        file_path=file_path,
        file_name=file.filename
    )
    
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)
    
    # Queue OCR processing if it's an image
    if file.content_type.startswith("image/"):
        await ocr_service.queue_ocr_processing(db_submission.id, file_path)
    
    return db_submission

@router.put("/{assignment_id}/submissions/{submission_id}/grade")
async def grade_submission(
    assignment_id: int,
    submission_id: int,
    grade: float = Form(...),
    feedback: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Grade a submission (teachers only)"""
    # Get submission
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.assignment_id == assignment_id
        )
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Update grade and feedback
    submission.grade = grade
    submission.feedback = feedback
    
    await db.commit()
    await db.refresh(submission)
    
    return {"message": "Submission graded successfully", "submission": submission}