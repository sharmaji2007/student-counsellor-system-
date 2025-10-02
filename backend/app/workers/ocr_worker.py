"""
Worker functions for processing OCR and quiz generation tasks
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models import Submission, QuizQuestion
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

ocr_service = OCRService()
llm_service = LLMService()
storage_service = StorageService()

def process_submission_ocr(submission_id: int, file_path: str):
    """Process OCR for a submission and generate quiz questions"""
    asyncio.run(_process_submission_ocr_async(submission_id, file_path))

async def _process_submission_ocr_async(submission_id: int, file_path: str):
    """Async version of OCR processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()
            
            if not submission:
                print(f"Submission {submission_id} not found")
                return
            
            # Download file from storage
            file_content = await storage_service.download_file(file_path)
            if not file_content:
                print(f"Could not download file: {file_path}")
                return
            
            # Extract text using OCR
            print(f"Processing OCR for submission {submission_id}")
            ocr_result = ocr_service.extract_text_sync(file_content)
            
            if not ocr_result["text"]:
                print(f"No text extracted from {file_path}")
                return
            
            # Update submission with OCR text
            await db.execute(
                update(Submission)
                .where(Submission.id == submission_id)
                .values(ocr_text=ocr_result["text"])
            )
            
            # Generate quiz questions
            print(f"Generating quiz for submission {submission_id}")
            quiz_result = llm_service.generate_quiz_sync(ocr_result["text"], 5)
            
            # Save quiz questions
            for question_data in quiz_result["questions"]:
                quiz_question = QuizQuestion(
                    submission_id=submission_id,
                    question=question_data["question"],
                    options=question_data["options"],
                    correct_answer=question_data["correct_answer"],
                    explanation=question_data.get("explanation")
                )
                db.add(quiz_question)
            
            await db.commit()
            print(f"Successfully processed submission {submission_id}")
            
        except Exception as e:
            print(f"Error processing submission {submission_id}: {e}")
            await db.rollback()

def send_notification(recipient: str, message: str, notification_type: str = "sms"):
    """Send notification (SMS/Email)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService()
    
    if notification_type == "sms":
        notification_service.send_sms_sync(recipient, message)
    elif notification_type == "email":
        # Email sending would be implemented here
        print(f"Mock email to {recipient}: {message}")
    else:
        print(f"Unknown notification type: {notification_type}")

def calculate_weekly_risk_digest():
    """Calculate and send weekly risk digest to mentors"""
    asyncio.run(_calculate_weekly_risk_digest_async())

async def _calculate_weekly_risk_digest_async():
    """Async version of weekly risk digest calculation"""
    from app.services.risk_service import RiskService
    from app.services.notification_service import NotificationService
    
    risk_service = RiskService()
    notification_service = NotificationService()
    
    async with AsyncSessionLocal() as db:
        try:
            # Get high-risk students
            from app.models import User, RiskScore, RiskLevel
            
            result = await db.execute(
                select(User, RiskScore)
                .join(RiskScore, User.id == RiskScore.student_id)
                .where(RiskScore.risk_level == RiskLevel.RED)
                .order_by(RiskScore.calculated_at.desc())
            )
            
            high_risk_data = []
            for user, risk_score in result.fetchall():
                high_risk_data.append({
                    "name": user.full_name,
                    "risk_level": risk_score.risk_level.value,
                    "score": risk_score.overall_score,
                    "issues": "Multiple risk factors detected"
                })
            
            if high_risk_data:
                # Send to mentors (mock implementation)
                mentor_contacts = [
                    {"phone": "+1234567890", "email": "mentor@school.edu"}
                ]
                
                for contact in mentor_contacts:
                    await notification_service.send_weekly_risk_digest(
                        contact["phone"],
                        contact["email"],
                        high_risk_data
                    )
                
                print(f"Sent weekly risk digest for {len(high_risk_data)} high-risk students")
            else:
                print("No high-risk students found for weekly digest")
                
        except Exception as e:
            print(f"Error generating weekly risk digest: {e}")

# RQ job functions (these are the actual functions called by the worker)
def ocr_job(submission_id: int, file_path: str):
    """RQ job wrapper for OCR processing"""
    process_submission_ocr(submission_id, file_path)

def notification_job(recipient: str, message: str, notification_type: str = "sms"):
    """RQ job wrapper for notifications"""
    send_notification(recipient, message, notification_type)

def weekly_digest_job():
    """RQ job wrapper for weekly digest"""
    calculate_weekly_risk_digest()