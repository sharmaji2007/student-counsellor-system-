#!/usr/bin/env python3
"""
Seed script to populate the database with sample data for development and testing.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from faker import Faker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import (
    User, UserRole, StudentProfile, Assignment, AttendanceRecord, 
    TestRecord, FeeRecord, RiskScore, RiskLevel
)

fake = Faker()

async def create_users():
    """Create sample users with different roles"""
    users_data = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "phone": "+1234567890"
        },
        {
            "email": "teacher@example.com", 
            "password": "teacher123",
            "full_name": "John Teacher",
            "role": UserRole.TEACHER,
            "phone": "+1234567891"
        },
        {
            "email": "counselor@example.com",
            "password": "counselor123", 
            "full_name": "Sarah Counselor",
            "role": UserRole.COUNSELOR,
            "phone": "+1234567892"
        }
    ]
    
    # Create 5 sample students
    for i in range(5):
        users_data.append({
            "email": f"student{i+1}@example.com",
            "password": "student123",
            "full_name": fake.name(),
            "role": UserRole.STUDENT,
            "phone": fake.phone_number()
        })
    
    users = []
    for user_data in users_data:
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone=user_data["phone"]
        )
        users.append(user)
    
    return users

async def create_student_profiles(students):
    """Create student profiles for student users"""
    profiles = []
    classes = ["10A", "10B", "11A", "11B", "12A"]
    
    for i, student in enumerate(students):
        profile = StudentProfile(
            user_id=student.id,
            student_id=f"STU{2024}{str(i+1).zfill(3)}",
            class_name=fake.random_element(classes),
            grade=fake.random_element(["10", "11", "12"]),
            guardian_name=fake.name(),
            guardian_phone=fake.phone_number(),
            guardian_email=fake.email()
        )
        profiles.append(profile)
    
    return profiles

async def create_assignments(teacher):
    """Create sample assignments"""
    assignments = []
    subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English"]
    
    for i in range(10):
        assignment = Assignment(
            title=f"{fake.random_element(subjects)} Assignment {i+1}",
            description=fake.text(max_nb_chars=200),
            teacher_id=teacher.id,
            class_name=fake.random_element(["10A", "10B", "11A"]),
            due_date=fake.date_time_between(start_date="+1d", end_date="+30d")
        )
        assignments.append(assignment)
    
    return assignments

async def create_attendance_records(profiles):
    """Create attendance records for students"""
    records = []
    
    for profile in profiles:
        # Create 30 days of attendance records
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            # 85% attendance rate on average
            present = fake.boolean(chance_of_getting_true=85)
            
            record = AttendanceRecord(
                student_id=profile.id,
                date=date,
                present=present
            )
            records.append(record)
    
    return records

async def create_test_records(profiles):
    """Create test records for students"""
    records = []
    subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English"]
    
    for profile in profiles:
        # Create 10 test records per student
        for i in range(10):
            max_score = fake.random_element([50, 75, 100])
            # Vary performance by student (some high, some low performers)
            if profile.id % 3 == 0:  # Low performer
                score = fake.random_int(min=20, max=int(max_score * 0.6))
            elif profile.id % 3 == 1:  # Average performer  
                score = fake.random_int(min=int(max_score * 0.5), max=int(max_score * 0.8))
            else:  # High performer
                score = fake.random_int(min=int(max_score * 0.7), max=max_score)
            
            record = TestRecord(
                student_id=profile.id,
                subject=fake.random_element(subjects),
                test_name=f"Test {i+1}",
                score=score,
                max_score=max_score,
                test_date=fake.date_time_between(start_date="-60d", end_date="now")
            )
            records.append(record)
    
    return records

async def create_fee_records(profiles):
    """Create fee records for students"""
    records = []
    
    for profile in profiles:
        # Create 3 fee records per student
        for i in range(3):
            due_date = fake.date_time_between(start_date="-30d", end_date="+30d")
            is_paid = fake.boolean(chance_of_getting_true=70)  # 70% payment rate
            
            record = FeeRecord(
                student_id=profile.id,
                amount=fake.random_element([500, 750, 1000, 1250]),
                due_date=due_date,
                paid_date=fake.date_time_between(start_date=due_date, end_date="now") if is_paid else None,
                is_paid=is_paid
            )
            records.append(record)
    
    return records

async def create_risk_scores(students):
    """Create risk scores for students"""
    scores = []
    
    for student in students:
        # Create varying risk levels
        if student.id % 5 == 0:  # High risk
            attendance_score = fake.random_int(min=60, max=100) / 100
            test_score = fake.random_int(min=60, max=100) / 100
            fee_score = fake.random_int(min=50, max=100) / 100
            chat_score = fake.random_int(min=40, max=80) / 100
            risk_level = RiskLevel.RED
        elif student.id % 5 == 1:  # Medium risk
            attendance_score = fake.random_int(min=30, max=70) / 100
            test_score = fake.random_int(min=30, max=70) / 100
            fee_score = fake.random_int(min=20, max=60) / 100
            chat_score = fake.random_int(min=10, max=50) / 100
            risk_level = RiskLevel.AMBER
        else:  # Low risk
            attendance_score = fake.random_int(min=0, max=40) / 100
            test_score = fake.random_int(min=0, max=40) / 100
            fee_score = fake.random_int(min=0, max=30) / 100
            chat_score = fake.random_int(min=0, max=20) / 100
            risk_level = RiskLevel.GREEN
        
        overall_score = (attendance_score + test_score + fee_score + chat_score) / 4
        
        score = RiskScore(
            student_id=student.id,
            attendance_score=attendance_score,
            test_score=test_score,
            fee_score=fee_score,
            chat_score=chat_score,
            overall_score=overall_score,
            risk_level=risk_level
        )
        scores.append(score)
    
    return scores

async def main():
    """Main function to seed the database"""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Create users
            print("👥 Creating users...")
            users = await create_users()
            db.add_all(users)
            await db.commit()
            
            # Refresh to get IDs
            for user in users:
                await db.refresh(user)
            
            # Separate users by role
            students = [u for u in users if u.role == UserRole.STUDENT]
            teacher = next(u for u in users if u.role == UserRole.TEACHER)
            
            # Create student profiles
            print("📋 Creating student profiles...")
            profiles = await create_student_profiles(students)
            db.add_all(profiles)
            await db.commit()
            
            # Refresh profiles to get IDs
            for profile in profiles:
                await db.refresh(profile)
            
            # Create assignments
            print("📚 Creating assignments...")
            assignments = await create_assignments(teacher)
            db.add_all(assignments)
            await db.commit()
            
            # Create attendance records
            print("📅 Creating attendance records...")
            attendance_records = await create_attendance_records(profiles)
            db.add_all(attendance_records)
            await db.commit()
            
            # Create test records
            print("📝 Creating test records...")
            test_records = await create_test_records(profiles)
            db.add_all(test_records)
            await db.commit()
            
            # Create fee records
            print("💰 Creating fee records...")
            fee_records = await create_fee_records(profiles)
            db.add_all(fee_records)
            await db.commit()
            
            # Create risk scores
            print("⚠️ Creating risk scores...")
            risk_scores = await create_risk_scores(students)
            db.add_all(risk_scores)
            await db.commit()
            
            print("✅ Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   • Users: {len(users)}")
            print(f"   • Student Profiles: {len(profiles)}")
            print(f"   • Assignments: {len(assignments)}")
            print(f"   • Attendance Records: {len(attendance_records)}")
            print(f"   • Test Records: {len(test_records)}")
            print(f"   • Fee Records: {len(fee_records)}")
            print(f"   • Risk Scores: {len(risk_scores)}")
            
            print("\n🔑 Login Credentials:")
            print("   • Admin: admin@example.com / admin123")
            print("   • Teacher: teacher@example.com / teacher123")
            print("   • Counselor: counselor@example.com / counselor123")
            print("   • Students: student1@example.com to student5@example.com / student123")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())