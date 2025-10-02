from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user, get_teacher_user
from app.models import (
    User, StudentProfile, RiskScore, AttendanceRecord, 
    TestRecord, FeeRecord, ChatMessage, RiskLevel
)
from app.schemas import RiskScore as RiskScoreSchema
from app.services.risk_service import RiskService

router = APIRouter()
risk_service = RiskService()

@router.get("/scores", response_model=List[RiskScoreSchema])
async def get_risk_scores(
    risk_level: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get risk scores for all students (teachers and admins only)"""
    query = select(RiskScore).order_by(RiskScore.calculated_at.desc())
    
    if risk_level:
        try:
            level = RiskLevel(risk_level.lower())
            query = query.where(RiskScore.risk_level == level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid risk level. Use: green, amber, or red"
            )
    
    result = await db.execute(query)
    scores = result.scalars().all()
    return scores

@router.get("/scores/{student_id}", response_model=RiskScoreSchema)
async def get_student_risk_score(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk score for specific student"""
    # Students can only see their own score
    if current_user.role.value == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only view their own risk score"
        )
    
    # Get latest risk score
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.student_id == student_id)
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    
    risk_score = result.scalar_one_or_none()
    if not risk_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk score not found"
        )
    
    return risk_score

@router.post("/calculate/{student_id}", response_model=RiskScoreSchema)
async def calculate_risk_score(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Calculate and store risk score for a student"""
    # Verify student exists
    student_result = await db.execute(
        select(User).where(User.id == student_id, User.role == "student")
    )
    student = student_result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get student profile
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Calculate risk score
    risk_data = await risk_service.calculate_student_risk(db, student_id, profile.id)
    
    # Create new risk score record
    db_risk_score = RiskScore(
        student_id=student_id,
        attendance_score=risk_data["attendance_score"],
        test_score=risk_data["test_score"],
        fee_score=risk_data["fee_score"],
        chat_score=risk_data["chat_score"],
        overall_score=risk_data["overall_score"],
        risk_level=risk_data["risk_level"]
    )
    
    db.add(db_risk_score)
    await db.commit()
    await db.refresh(db_risk_score)
    
    return db_risk_score

@router.post("/calculate-all")
async def calculate_all_risk_scores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Calculate risk scores for all students"""
    # Get all students
    students_result = await db.execute(
        select(User).where(User.role == "student", User.is_active == True)
    )
    students = students_result.scalars().all()
    
    calculated_count = 0
    errors = []
    
    for student in students:
        try:
            # Get student profile
            profile_result = await db.execute(
                select(StudentProfile).where(StudentProfile.user_id == student.id)
            )
            profile = profile_result.scalar_one_or_none()
            
            if not profile:
                errors.append(f"No profile found for student {student.id}")
                continue
            
            # Calculate risk score
            risk_data = await risk_service.calculate_student_risk(db, student.id, profile.id)
            
            # Create new risk score record
            db_risk_score = RiskScore(
                student_id=student.id,
                attendance_score=risk_data["attendance_score"],
                test_score=risk_data["test_score"],
                fee_score=risk_data["fee_score"],
                chat_score=risk_data["chat_score"],
                overall_score=risk_data["overall_score"],
                risk_level=risk_data["risk_level"]
            )
            
            db.add(db_risk_score)
            calculated_count += 1
            
        except Exception as e:
            errors.append(f"Error calculating risk for student {student.id}: {str(e)}")
    
    await db.commit()
    
    return {
        "message": f"Calculated risk scores for {calculated_count} students",
        "calculated_count": calculated_count,
        "total_students": len(students),
        "errors": errors
    }

@router.get("/dashboard/summary")
async def get_risk_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get risk dashboard summary with counts by risk level"""
    # Get latest risk scores for each student
    subquery = (
        select(
            RiskScore.student_id,
            func.max(RiskScore.calculated_at).label("latest_date")
        )
        .group_by(RiskScore.student_id)
        .subquery()
    )
    
    # Get risk level counts
    result = await db.execute(
        select(RiskScore.risk_level, func.count(RiskScore.id))
        .join(
            subquery,
            and_(
                RiskScore.student_id == subquery.c.student_id,
                RiskScore.calculated_at == subquery.c.latest_date
            )
        )
        .group_by(RiskScore.risk_level)
    )
    
    risk_counts = dict(result.fetchall())
    
    # Get high-risk students (RED level)
    high_risk_result = await db.execute(
        select(RiskScore, User.full_name)
        .join(User, RiskScore.student_id == User.id)
        .join(
            subquery,
            and_(
                RiskScore.student_id == subquery.c.student_id,
                RiskScore.calculated_at == subquery.c.latest_date
            )
        )
        .where(RiskScore.risk_level == RiskLevel.RED)
        .order_by(RiskScore.overall_score.desc())
        .limit(10)
    )
    
    high_risk_students = []
    for risk_score, student_name in high_risk_result.fetchall():
        high_risk_students.append({
            "student_id": risk_score.student_id,
            "student_name": student_name,
            "overall_score": risk_score.overall_score,
            "risk_level": risk_score.risk_level,
            "calculated_at": risk_score.calculated_at
        })
    
    return {
        "risk_counts": {
            "green": risk_counts.get(RiskLevel.GREEN, 0),
            "amber": risk_counts.get(RiskLevel.AMBER, 0),
            "red": risk_counts.get(RiskLevel.RED, 0)
        },
        "high_risk_students": high_risk_students,
        "total_students": sum(risk_counts.values())
    }