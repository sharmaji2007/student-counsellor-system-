from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models import (
    AttendanceRecord, TestRecord, FeeRecord, ChatMessage, 
    RiskLevel, SOSIncident
)

class RiskService:
    def __init__(self):
        self.weights = {
            "attendance": 0.3,
            "test_performance": 0.25,
            "fee_payment": 0.2,
            "chat_behavior": 0.25
        }
    
    async def calculate_student_risk(
        self, 
        db: AsyncSession, 
        student_id: int, 
        profile_id: int
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk score for a student"""
        
        # Calculate individual risk components
        attendance_score = await self._calculate_attendance_risk(db, profile_id)
        test_score = await self._calculate_test_performance_risk(db, profile_id)
        fee_score = await self._calculate_fee_payment_risk(db, profile_id)
        chat_score = await self._calculate_chat_behavior_risk(db, student_id)
        
        # Calculate weighted overall score
        overall_score = (
            attendance_score * self.weights["attendance"] +
            test_score * self.weights["test_performance"] +
            fee_score * self.weights["fee_payment"] +
            chat_score * self.weights["chat_behavior"]
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        return {
            "attendance_score": attendance_score,
            "test_score": test_score,
            "fee_score": fee_score,
            "chat_score": chat_score,
            "overall_score": overall_score,
            "risk_level": risk_level
        }
    
    async def _calculate_attendance_risk(self, db: AsyncSession, profile_id: int) -> float:
        """Calculate attendance-based risk score (0.0 = low risk, 1.0 = high risk)"""
        # Get attendance records for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = await db.execute(
            select(
                func.count(AttendanceRecord.id).label("total_days"),
                func.sum(func.cast(AttendanceRecord.present, db.Integer)).label("present_days")
            )
            .where(
                and_(
                    AttendanceRecord.student_id == profile_id,
                    AttendanceRecord.date >= thirty_days_ago
                )
            )
        )
        
        attendance_data = result.first()
        
        if not attendance_data or attendance_data.total_days == 0:
            return 0.5  # Neutral score if no data
        
        attendance_rate = attendance_data.present_days / attendance_data.total_days
        
        # Convert attendance rate to risk score (inverse relationship)
        if attendance_rate >= 0.95:
            return 0.0  # Excellent attendance = low risk
        elif attendance_rate >= 0.85:
            return 0.2  # Good attendance = low risk
        elif attendance_rate >= 0.75:
            return 0.4  # Fair attendance = medium risk
        elif attendance_rate >= 0.60:
            return 0.7  # Poor attendance = high risk
        else:
            return 1.0  # Very poor attendance = very high risk
    
    async def _calculate_test_performance_risk(self, db: AsyncSession, profile_id: int) -> float:
        """Calculate test performance-based risk score"""
        # Get test records for the last 60 days
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        result = await db.execute(
            select(
                func.avg(TestRecord.score / TestRecord.max_score).label("avg_percentage"),
                func.count(TestRecord.id).label("test_count")
            )
            .where(
                and_(
                    TestRecord.student_id == profile_id,
                    TestRecord.test_date >= sixty_days_ago
                )
            )
        )
        
        test_data = result.first()
        
        if not test_data or test_data.test_count == 0:
            return 0.5  # Neutral score if no data
        
        avg_percentage = test_data.avg_percentage or 0.0
        
        # Convert test performance to risk score (inverse relationship)
        if avg_percentage >= 0.85:
            return 0.0  # Excellent performance = low risk
        elif avg_percentage >= 0.75:
            return 0.2  # Good performance = low risk
        elif avg_percentage >= 0.60:
            return 0.4  # Fair performance = medium risk
        elif avg_percentage >= 0.45:
            return 0.7  # Poor performance = high risk
        else:
            return 1.0  # Very poor performance = very high risk
    
    async def _calculate_fee_payment_risk(self, db: AsyncSession, profile_id: int) -> float:
        """Calculate fee payment-based risk score"""
        # Get overdue fees
        current_date = datetime.utcnow()
        
        result = await db.execute(
            select(
                func.count(FeeRecord.id).label("total_fees"),
                func.sum(func.cast(FeeRecord.is_paid, db.Integer)).label("paid_fees"),
                func.count(
                    func.case(
                        (and_(FeeRecord.is_paid == False, FeeRecord.due_date < current_date), 1)
                    )
                ).label("overdue_fees")
            )
            .where(FeeRecord.student_id == profile_id)
        )
        
        fee_data = result.first()
        
        if not fee_data or fee_data.total_fees == 0:
            return 0.0  # No fees = low risk
        
        overdue_count = fee_data.overdue_fees or 0
        total_count = fee_data.total_fees or 1
        
        overdue_ratio = overdue_count / total_count
        
        # Convert overdue ratio to risk score
        if overdue_ratio == 0:
            return 0.0  # No overdue fees = low risk
        elif overdue_ratio <= 0.2:
            return 0.3  # Few overdue fees = low-medium risk
        elif overdue_ratio <= 0.5:
            return 0.6  # Some overdue fees = medium-high risk
        else:
            return 1.0  # Many overdue fees = high risk
    
    async def _calculate_chat_behavior_risk(self, db: AsyncSession, student_id: int) -> float:
        """Calculate chat behavior-based risk score"""
        # Get chat messages for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Count total messages and flagged messages
        total_result = await db.execute(
            select(func.count(ChatMessage.id))
            .where(
                and_(
                    ChatMessage.user_id == student_id,
                    ChatMessage.created_at >= thirty_days_ago
                )
            )
        )
        
        flagged_result = await db.execute(
            select(func.count(ChatMessage.id))
            .where(
                and_(
                    ChatMessage.user_id == student_id,
                    ChatMessage.created_at >= thirty_days_ago,
                    ChatMessage.flagged_for_sos == True
                )
            )
        )
        
        # Check for recent SOS incidents
        sos_result = await db.execute(
            select(func.count(SOSIncident.id))
            .where(
                and_(
                    SOSIncident.student_id == student_id,
                    SOSIncident.created_at >= thirty_days_ago
                )
            )
        )
        
        total_messages = total_result.scalar() or 0
        flagged_messages = flagged_result.scalar() or 0
        sos_incidents = sos_result.scalar() or 0
        
        # Calculate risk based on flagged content and SOS incidents
        if sos_incidents > 0:
            return 1.0  # Any SOS incident = high risk
        
        if total_messages == 0:
            return 0.3  # No communication might indicate withdrawal
        
        flagged_ratio = flagged_messages / total_messages
        
        if flagged_ratio == 0:
            return 0.0  # No flagged messages = low risk
        elif flagged_ratio <= 0.1:
            return 0.4  # Few flagged messages = medium risk
        elif flagged_ratio <= 0.3:
            return 0.7  # Some flagged messages = high risk
        else:
            return 1.0  # Many flagged messages = very high risk
    
    def _determine_risk_level(self, overall_score: float) -> RiskLevel:
        """Determine risk level based on overall score"""
        if overall_score >= 0.7:
            return RiskLevel.RED
        elif overall_score >= 0.4:
            return RiskLevel.AMBER
        else:
            return RiskLevel.GREEN
    
    async def get_risk_factors_explanation(
        self, 
        db: AsyncSession, 
        student_id: int, 
        profile_id: int
    ) -> Dict[str, Any]:
        """Get detailed explanation of risk factors"""
        
        # Get individual scores
        attendance_score = await self._calculate_attendance_risk(db, profile_id)
        test_score = await self._calculate_test_performance_risk(db, profile_id)
        fee_score = await self._calculate_fee_payment_risk(db, profile_id)
        chat_score = await self._calculate_chat_behavior_risk(db, student_id)
        
        factors = []
        
        # Attendance factors
        if attendance_score >= 0.7:
            factors.append("Poor attendance pattern detected")
        elif attendance_score >= 0.4:
            factors.append("Irregular attendance noted")
        
        # Test performance factors
        if test_score >= 0.7:
            factors.append("Declining academic performance")
        elif test_score >= 0.4:
            factors.append("Below-average test scores")
        
        # Fee payment factors
        if fee_score >= 0.6:
            factors.append("Multiple overdue fee payments")
        elif fee_score >= 0.3:
            factors.append("Some overdue payments")
        
        # Chat behavior factors
        if chat_score >= 0.7:
            factors.append("Concerning chat messages detected")
        elif chat_score >= 0.4:
            factors.append("Some flagged communications")
        
        return {
            "risk_factors": factors,
            "component_scores": {
                "attendance": attendance_score,
                "test_performance": test_score,
                "fee_payment": fee_score,
                "chat_behavior": chat_score
            },
            "recommendations": self._get_recommendations(factors)
        }
    
    def _get_recommendations(self, risk_factors: list) -> list:
        """Get recommendations based on risk factors"""
        recommendations = []
        
        if "Poor attendance pattern detected" in risk_factors:
            recommendations.append("Schedule meeting with student and parents about attendance")
        
        if "Declining academic performance" in risk_factors:
            recommendations.append("Arrange additional academic support or tutoring")
        
        if "Multiple overdue fee payments" in risk_factors:
            recommendations.append("Contact parents about fee payment arrangements")
        
        if "Concerning chat messages detected" in risk_factors:
            recommendations.append("Immediate counselor intervention required")
        
        if not recommendations:
            recommendations.append("Continue regular monitoring and support")
        
        return recommendations