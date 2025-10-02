from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user, get_admin_user, get_teacher_user
from app.models import User, StudentProfile, AttendanceRecord, TestRecord, FeeRecord, RiskScore, Submission
from app.schemas import (
    StudentProfile as StudentProfileSchema,
    StudentProfileCreate,
    StudentDashboard,
    AttendanceRecord as AttendanceRecordSchema,
    TestRecord as TestRecordSchema,
    FeeRecord as FeeRecordSchema
)

router = APIRouter()

@router.get("/", response_model=List[StudentProfileSchema])
async def get_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get all students (teachers and admins only)"""
    result = await db.execute(
        select(StudentProfile).options(selectinload(StudentProfile.user))
    )
    students = result.scalars().all()
    return students

@router.get("/me", response_model=StudentDashboard)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current student's dashboard"""
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get recent submissions
    submissions_result = await db.execute(
        select(Submission)
        .where(Submission.student_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(5)
    )
    recent_submissions = submissions_result.scalars().all()
    
    # Get recent attendance
    attendance_result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == profile.id)
        .order_by(AttendanceRecord.date.desc())
        .limit(10)
    )
    recent_attendance = attendance_result.scalars().all()
    
    # Get recent tests
    tests_result = await db.execute(
        select(TestRecord)
        .where(TestRecord.student_id == profile.id)
        .order_by(TestRecord.test_date.desc())
        .limit(5)
    )
    recent_tests = tests_result.scalars().all()
    
    # Get pending fees
    fees_result = await db.execute(
        select(FeeRecord)
        .where(FeeRecord.student_id == profile.id, FeeRecord.is_paid == False)
        .order_by(FeeRecord.due_date.asc())
    )
    pending_fees = fees_result.scalars().all()
    
    # Get current risk score
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.student_id == current_user.id)
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    current_risk_score = risk_result.scalar_one_or_none()
    
    return StudentDashboard(
        user=current_user,
        profile=profile,
        recent_submissions=recent_submissions,
        recent_attendance=recent_attendance,
        recent_tests=recent_tests,
        pending_fees=pending_fees,
        current_risk_score=current_risk_score
    )

@router.get("/{student_id}", response_model=StudentDashboard)
async def get_student_profile(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get specific student's profile (teachers and admins only)"""
    # Get student user
    user_result = await db.execute(select(User).where(User.id == student_id))
    student_user = user_result.scalar_one_or_none()
    
    if not student_user or student_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get student profile
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get recent submissions
    submissions_result = await db.execute(
        select(Submission)
        .where(Submission.student_id == student_id)
        .order_by(Submission.submitted_at.desc())
        .limit(5)
    )
    recent_submissions = submissions_result.scalars().all()
    
    # Get recent attendance
    attendance_result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == profile.id)
        .order_by(AttendanceRecord.date.desc())
        .limit(10)
    )
    recent_attendance = attendance_result.scalars().all()
    
    # Get recent tests
    tests_result = await db.execute(
        select(TestRecord)
        .where(TestRecord.student_id == profile.id)
        .order_by(TestRecord.test_date.desc())
        .limit(5)
    )
    recent_tests = tests_result.scalars().all()
    
    # Get pending fees
    fees_result = await db.execute(
        select(FeeRecord)
        .where(FeeRecord.student_id == profile.id, FeeRecord.is_paid == False)
        .order_by(FeeRecord.due_date.asc())
    )
    pending_fees = fees_result.scalars().all()
    
    # Get current risk score
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.student_id == student_id)
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    current_risk_score = risk_result.scalar_one_or_none()
    
    return StudentDashboard(
        user=student_user,
        profile=profile,
        recent_submissions=recent_submissions,
        recent_attendance=recent_attendance,
        recent_tests=recent_tests,
        pending_fees=pending_fees,
        current_risk_score=current_risk_score
    )

@router.post("/profile", response_model=StudentProfileSchema)
async def create_student_profile(
    profile_data: StudentProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create student profile (admin only)"""
    # Check if profile already exists
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == profile_data.user_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists"
        )
    
    # Create profile
    db_profile = StudentProfile(**profile_data.dict())
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    
    return db_profile