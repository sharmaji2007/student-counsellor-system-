import asyncio
from typing import List, Dict, Any
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

class NotificationService:
    def __init__(self):
        self.twilio_client = None
        self._initialize_twilio()
    
    def _initialize_twilio(self):
        """Initialize Twilio client"""
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                print(f"Warning: Could not initialize Twilio client: {e}")
        else:
            print("Warning: Twilio credentials not provided")
    
    async def send_sos_alert(
        self, 
        student_id: int, 
        student_name: str, 
        message: str, 
        keywords: List[str]
    ):
        """Send SOS alert to counselor and guardians"""
        alert_message = f"""
        🚨 URGENT: Student Safety Alert
        
        Student: {student_name} (ID: {student_id})
        Triggered Keywords: {', '.join(keywords)}
        Message: "{message}"
        
        Please contact the student immediately.
        Time: {asyncio.get_event_loop().time()}
        """
        
        # Send to counselor
        if settings.COUNSELOR_PHONE:
            await self._send_sms(settings.COUNSELOR_PHONE, alert_message)
        
        if settings.COUNSELOR_EMAIL:
            await self._send_email(
                settings.COUNSELOR_EMAIL,
                "URGENT: Student Safety Alert",
                alert_message
            )
        
        print(f"SOS alert sent for student {student_id}")
    
    async def send_weekly_risk_digest(
        self, 
        recipient_phone: str, 
        recipient_email: str, 
        high_risk_students: List[Dict[str, Any]]
    ):
        """Send weekly digest of high-risk students to mentors"""
        if not high_risk_students:
            return
        
        message = "📊 Weekly Student Risk Report\n\n"
        message += f"High-risk students requiring attention ({len(high_risk_students)}):\n\n"
        
        for student in high_risk_students:
            message += f"• {student['name']} - Risk Level: {student['risk_level']}\n"
            message += f"  Score: {student['score']:.2f} | Issues: {student['issues']}\n\n"
        
        message += "Please review and take appropriate action."
        
        # Send SMS
        if recipient_phone:
            await self._send_sms(recipient_phone, message)
        
        # Send Email
        if recipient_email:
            await self._send_email(
                recipient_email,
                "Weekly Student Risk Report",
                message
            )
    
    async def send_assignment_reminder(
        self, 
        student_phone: str, 
        student_email: str, 
        assignment_title: str, 
        due_date: str
    ):
        """Send assignment reminder to student"""
        message = f"""
        📚 Assignment Reminder
        
        Assignment: {assignment_title}
        Due Date: {due_date}
        
        Don't forget to submit your work on time!
        """
        
        if student_phone:
            await self._send_sms(student_phone, message)
        
        if student_email:
            await self._send_email(
                student_email,
                f"Reminder: {assignment_title}",
                message
            )
    
    async def _send_sms(self, phone_number: str, message: str):
        """Send SMS using Twilio"""
        if not self.twilio_client or not settings.TWILIO_PHONE_NUMBER:
            print(f"Mock SMS to {phone_number}: {message}")
            return
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print(f"SMS sent successfully: {message_obj.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")
    
    async def _send_email(self, email: str, subject: str, body: str):
        """Send email (mock implementation)"""
        # In production, you would use a proper email service like SendGrid, SES, etc.
        print(f"Mock Email to {email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print("---")
    
    async def send_push_notification(
        self, 
        user_token: str, 
        title: str, 
        body: str, 
        data: Dict[str, Any] = None
    ):
        """Send push notification using FCM"""
        # Mock implementation - in production, use Firebase Admin SDK
        print(f"Mock Push Notification to {user_token}")
        print(f"Title: {title}")
        print(f"Body: {body}")
        if data:
            print(f"Data: {data}")
        print("---")
    
    async def send_bulk_notification(
        self, 
        recipients: List[Dict[str, str]], 
        message: str, 
        subject: str = None
    ):
        """Send bulk notifications to multiple recipients"""
        tasks = []
        
        for recipient in recipients:
            if recipient.get('phone'):
                tasks.append(self._send_sms(recipient['phone'], message))
            
            if recipient.get('email') and subject:
                tasks.append(self._send_email(recipient['email'], subject, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def send_sms_sync(self, phone_number: str, message: str):
        """Synchronous SMS sending for worker processes"""
        if not self.twilio_client or not settings.TWILIO_PHONE_NUMBER:
            print(f"Mock SMS to {phone_number}: {message}")
            return
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print(f"SMS sent successfully: {message_obj.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")