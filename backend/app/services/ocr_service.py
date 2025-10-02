import asyncio
import time
from typing import Dict, Any
from google.cloud import vision
import io
import redis
from rq import Queue
import json

from app.core.config import settings

class OCRService:
    def __init__(self):
        self.client = None
        self.redis_conn = None
        self.queue = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Google Vision and Redis clients"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                self.client = vision.ImageAnnotatorClient()
            
            if settings.REDIS_URL:
                self.redis_conn = redis.from_url(settings.REDIS_URL)
                self.queue = Queue(connection=self.redis_conn)
        except Exception as e:
            print(f"Warning: Could not initialize OCR service: {e}")
    
    async def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image using Google Vision API"""
        start_time = time.time()
        
        if not self.client:
            # Fallback: return mock data for development
            await asyncio.sleep(1)  # Simulate processing time
            return {
                "text": "Sample extracted text from image. This is a mock response for development.",
                "confidence": 0.95,
                "processing_time": time.time() - start_time
            }
        
        try:
            # Create Vision API image object
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            # Extract text and confidence
            if texts:
                extracted_text = texts[0].description
                # Calculate average confidence from all detected text blocks
                total_confidence = sum([
                    vertex.confidence if hasattr(vertex, 'confidence') else 0.9 
                    for vertex in texts
                ])
                avg_confidence = total_confidence / len(texts) if texts else 0.0
            else:
                extracted_text = ""
                avg_confidence = 0.0
            
            processing_time = time.time() - start_time
            
            return {
                "text": extracted_text,
                "confidence": avg_confidence,
                "processing_time": processing_time
            }
            
        except Exception as e:
            # Return error with mock data for development
            return {
                "text": f"OCR processing failed: {str(e)}. Using mock data for development.",
                "confidence": 0.0,
                "processing_time": time.time() - start_time
            }
    
    async def queue_ocr_processing(self, submission_id: int, file_path: str):
        """Queue OCR processing job"""
        if not self.queue:
            print("Warning: Redis queue not available, skipping OCR job")
            return
        
        try:
            job = self.queue.enqueue(
                'app.workers.ocr_worker.process_submission_ocr',
                submission_id,
                file_path,
                job_timeout='5m'
            )
            print(f"Queued OCR job {job.id} for submission {submission_id}")
            return job.id
        except Exception as e:
            print(f"Failed to queue OCR job: {e}")
            return None
    
    def extract_text_sync(self, image_data: bytes) -> Dict[str, Any]:
        """Synchronous version for worker processes"""
        start_time = time.time()
        
        if not self.client:
            # Mock response for development
            time.sleep(1)
            return {
                "text": "Sample extracted text from image. This is a mock response for development.",
                "confidence": 0.95,
                "processing_time": time.time() - start_time
            }
        
        try:
            image = vision.Image(content=image_data)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            if texts:
                extracted_text = texts[0].description
                total_confidence = sum([
                    vertex.confidence if hasattr(vertex, 'confidence') else 0.9 
                    for vertex in texts
                ])
                avg_confidence = total_confidence / len(texts) if texts else 0.0
            else:
                extracted_text = ""
                avg_confidence = 0.0
            
            processing_time = time.time() - start_time
            
            return {
                "text": extracted_text,
                "confidence": avg_confidence,
                "processing_time": processing_time
            }
            
        except Exception as e:
            return {
                "text": f"OCR processing failed: {str(e)}",
                "confidence": 0.0,
                "processing_time": time.time() - start_time
            }