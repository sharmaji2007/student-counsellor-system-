from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import UserRole, RiskLevel

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Student Profile Schemas
class StudentProfileBase(BaseModel):
    student_id: str
    class_name: str
    grade: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[EmailStr] = None

class StudentProfileCreate(StudentProfileBase):
    user_id: int

class StudentProfile(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Assignment Schemas
class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    class_name: str
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int
    teacher_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Submission Schemas
class SubmissionBase(BaseModel):
    assignment_id: int
    file_name: str

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    id: int
    student_id: int
    file_path: str
    ocr_text: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Quiz Question Schemas
class QuizQuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class QuizQuestion(QuizQuestionBase):
    id: int
    submission_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Message Schemas
class ChatMessageBase(BaseModel):
    message: str
    is_private: bool = True

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    flagged_for_sos: bool
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Attendance Record Schemas
class AttendanceRecordBase(BaseModel):
    date: datetime
    present: bool

class AttendanceRecordCreate(AttendanceRecordBase):
    student_id: int

class AttendanceRecord(AttendanceRecordBase):
    id: int
    student_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Test Record Schemas
class TestRecordBase(BaseModel):
    subject: str
    test_name: str
    score: float
    max_score: float
    test_date: datetime

class TestRecordCreate(TestRecordBase):
    student_id: int

class TestRecord(TestRecordBase):
    id: int
    student_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Fee Record Schemas
class FeeRecordBase(BaseModel):
    amount: float
    due_date: datetime
    paid_date: Optional[datetime] = None
    is_paid: bool = False

class FeeRecordCreate(FeeRecordBase):
    student_id: int

class FeeRecord(FeeRecordBase):
    id: int
    student_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Risk Score Schemas
class RiskScoreBase(BaseModel):
    attendance_score: float
    test_score: float
    fee_score: float
    chat_score: float
    overall_score: float
    risk_level: RiskLevel

class RiskScore(RiskScoreBase):
    id: int
    student_id: int
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Student Dashboard Schema
class StudentDashboard(BaseModel):
    user: User
    profile: StudentProfile
    recent_submissions: List[Submission]
    recent_attendance: List[AttendanceRecord]
    recent_tests: List[TestRecord]
    pending_fees: List[FeeRecord]
    current_risk_score: Optional[RiskScore] = None

# SOS Incident Schemas
class SOSIncidentBase(BaseModel):
    trigger_keywords: List[str]
    status: str = "open"
    notes: Optional[str] = None

class SOSIncident(SOSIncidentBase):
    id: int
    student_id: int
    message_id: int
    counselor_notified: bool
    guardian_notified: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# OCR Response Schema
class OCRResponse(BaseModel):
    text: str
    confidence: float
    processing_time: float

# Quiz Generation Response
class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestion]
    total_questions: int
    generation_time: float

# File Upload Response
class FileUploadResponse(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    content_type: str
    upload_time: datetime

# Error Response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()

# Success Response
class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()