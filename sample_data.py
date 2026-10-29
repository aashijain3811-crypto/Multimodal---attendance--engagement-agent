"""
Sample Data Generator Module for Multimodal Attendance & Engagement Agent.
Populates the SQLite database with realistic college student rosters, 
multi-week classroom sessions, attendance logs, and multimodal engagement metrics.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from database import (
    init_db, reset_database, get_connection,
    add_student, create_session, mark_attendance_batch, record_engagement_batch
)
from agent import MultimodalEngagementAgent
from config import COURSES, DEPARTMENTS

SAMPLE_STUDENTS = [
    # Top Achievers
    {"roll": "2024-CS-101", "name": "Aarav Sharma", "email": "aarav.sharma@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section A", "archetype": "star"},
    {"roll": "2024-CS-102", "name": "Ananya Patel", "email": "ananya.patel@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section A", "archetype": "star"},
    {"roll": "2024-AI-103", "name": "Rohan Gupta", "email": "rohan.gupta@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section A", "archetype": "star"},
    {"roll": "2024-DS-104", "name": "Diya Sundaram", "email": "diya.sundaram@college.edu", "dept": "Data Science", "sem": "Semester 6", "sec": "Section A", "archetype": "star"},
    
    # Active Participants
    {"roll": "2024-CS-105", "name": "Vikramaditya Roy", "email": "vikram.roy@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section A", "archetype": "active"},
    {"roll": "2024-CS-106", "name": "Pooja Hegde", "email": "pooja.hegde@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section A", "archetype": "active"},
    {"roll": "2024-AI-107", "name": "Kabir Mehta", "email": "kabir.mehta@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section A", "archetype": "active"},
    {"roll": "2024-DS-108", "name": "Sneha Kulkarni", "email": "sneha.k@college.edu", "dept": "Data Science", "sem": "Semester 6", "sec": "Section A", "archetype": "active"},
    {"roll": "2024-IT-109", "name": "Arjun Nair", "email": "arjun.nair@college.edu", "dept": "Information Technology", "sem": "Semester 6", "sec": "Section A", "archetype": "active"},

    # Passive / Quiet Observers (High attendance, low speech)
    {"roll": "2024-CS-110", "name": "Tanvi Joshi", "email": "tanvi.joshi@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section B", "archetype": "quiet"},
    {"roll": "2024-AI-111", "name": "Karthik Raja", "email": "karthik.raja@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section B", "archetype": "quiet"},
    {"roll": "2024-DS-112", "name": "Meera Chawla", "email": "meera.chawla@college.edu", "dept": "Data Science", "sem": "Semester 6", "sec": "Section B", "archetype": "quiet"},
    {"roll": "2024-IT-113", "name": "Siddharth Verma", "email": "siddharth.v@college.edu", "dept": "Information Technology", "sem": "Semester 6", "sec": "Section B", "archetype": "quiet"},
    
    # Inconsistent / Moderate (Near threshold)
    {"roll": "2024-CS-114", "name": "Aditya Rao", "email": "aditya.rao@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section B", "archetype": "moderate"},
    {"roll": "2024-AI-115", "name": "Bhavna Swaminathan", "email": "bhavna.s@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section B", "archetype": "moderate"},
    {"roll": "2024-DS-116", "name": "Gaurav Sen", "email": "gaurav.sen@college.edu", "dept": "Data Science", "sem": "Semester 6", "sec": "Section B", "archetype": "moderate"},
    {"roll": "2024-IT-117", "name": "Ishaan Mukherjee", "email": "ishaan.m@college.edu", "dept": "Information Technology", "sem": "Semester 6", "sec": "Section B", "archetype": "moderate"},
    
    # Capable but Skips (Good MEI when present, but low attendance)
    {"roll": "2024-CS-118", "name": "Rhea Kapoor", "email": "rhea.kapoor@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section C", "archetype": "truant_smart"},
    {"roll": "2024-AI-119", "name": "Nikhil Agarwal", "email": "nikhil.a@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section C", "archetype": "truant_smart"},

    # Critical At-Risk (<75% attendance and disengaged)
    {"roll": "2024-CS-120", "name": "Devansh Singhania", "email": "devansh.s@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section C", "archetype": "critical"},
    {"roll": "2024-DS-121", "name": "Kavya Nambiar", "email": "kavya.n@college.edu", "dept": "Data Science", "sem": "Semester 6", "sec": "Section C", "archetype": "critical"},
    {"roll": "2024-IT-122", "name": "Sameer Khan", "email": "sameer.khan@college.edu", "dept": "Information Technology", "sem": "Semester 6", "sec": "Section C", "archetype": "critical"},
    {"roll": "2024-AI-123", "name": "Priyanka Desai", "email": "priyanka.d@college.edu", "dept": "Artificial Intelligence & Machine Learning", "sem": "Semester 6", "sec": "Section C", "archetype": "critical"},
    
    # Additional steady students
    {"roll": "2024-CS-124", "name": "Yashwant Reddy", "email": "yashwant.r@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section C", "archetype": "active"},
    {"roll": "2024-CS-125", "name": "Zoya Akhtar", "email": "zoya.a@college.edu", "dept": "Computer Science & Engineering", "sem": "Semester 6", "sec": "Section C", "archetype": "active"}
]

def generate_session_dates(num_sessions: int = 14) -> List[str]:
    """Generates sequential historical lecture dates spanning past weeks."""
    dates = []
    current_date = datetime.now() - timedelta(days=28)
    while len(dates) < num_sessions:
        # Monday to Friday only
        if current_date.weekday() < 5:
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return dates

def seed_database():
    """Wipes and populates realistic demo database."""
    reset_database()
    agent = MultimodalEngagementAgent()

    # 1. Insert Students
    student_id_map = {} # roll -> id
    for s in SAMPLE_STUDENTS:
        success, msg = add_student(
            roll_number=s["roll"],
            name=s["name"],
            email=s["email"],
            department=s["dept"],
            semester=s["sem"],
            section=s["sec"]
        )
    
    # Retrieve generated IDs
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, roll_number FROM students")
    for row in cursor.fetchall():
        student_id_map[row["roll_number"]] = row["id"]
    conn.close()

    # 2. Create Classroom Sessions
    session_dates = generate_session_dates(num_sessions=14)
    sessions_list = []
    
    for i, date_str in enumerate(session_dates):
        course = COURSES[i % len(COURSES)]
        sess_id = create_session(
            course=course,
            session_date=date_str,
            session_time="10:00 AM" if i % 2 == 0 else "02:00 PM",
            teacher="Prof. Dr. R. Sharma" if i % 2 == 0 else "Dr. Sunita Sen",
            notes=f"Lecture Unit #{((i % 5) + 1)}: Core Topics & Case Study Discussion."
        )
        sessions_list.append(sess_id)

    # 3. Populate Attendance and Multimodal Scores per Student
    random.seed(42) # Consistent, reproducible demo data

    for s_meta in SAMPLE_STUDENTS:
        roll = s_meta["roll"]
        s_id = student_id_map[roll]
        archetype = s_meta["archetype"]

        for sess_id in sessions_list:
            # Determine attendance based on archetype
            if archetype == "star":
                # 95% attendance
                status = "Present" if random.random() < 0.95 else random.choice(["Late", "Excused"])
            elif archetype == "active":
                # 85% attendance
                status = "Present" if random.random() < 0.85 else random.choice(["Absent", "Late"])
            elif archetype == "quiet":
                # 90% attendance, quiet participation
                status = "Present" if random.random() < 0.90 else "Absent"
            elif archetype == "moderate":
                # 76-80% attendance
                status = "Present" if random.random() < 0.78 else random.choice(["Absent", "Late"])
            elif archetype == "truant_smart":
                # 64% attendance (detention risk), but high score when present
                status = "Present" if random.random() < 0.64 else "Absent"
            elif archetype == "critical":
                # 50-60% attendance (severe detention risk)
                status = "Present" if random.random() < 0.55 else "Absent"
            else:
                status = "Present" if random.random() < 0.8 else "Absent"

            face_verified = 1 if status == "Present" and random.random() < 0.75 else 0

            # Log attendance
            mark_attendance_batch(sess_id, [{
                "student_id": s_id,
                "status": status,
                "face_verified": face_verified,
                "remarks": "On-time arrival" if status == "Present" else ("Arrived 15m late" if status == "Late" else "Unexcused absence")
            }])

            # Generate realistic Multimodal Engagement Metrics
            if status == "Absent":
                vis, aud, beh = 0.0, 0.0, 0.0
            else:
                if archetype == "star":
                    vis = round(random.uniform(82, 98), 1)
                    aud = round(random.uniform(80, 95), 1)
                    beh = round(random.uniform(85, 99), 1)
                elif archetype == "active":
                    vis = round(random.uniform(70, 88), 1)
                    aud = round(random.uniform(65, 85), 1)
                    beh = round(random.uniform(68, 88), 1)
                elif archetype == "quiet":
                    vis = round(random.uniform(75, 92), 1)
                    aud = round(random.uniform(25, 48), 1) # Low verbal participation!
                    beh = round(random.uniform(70, 85), 1)
                elif archetype == "moderate":
                    vis = round(random.uniform(55, 72), 1)
                    aud = round(random.uniform(45, 65), 1)
                    beh = round(random.uniform(50, 70), 1)
                elif archetype == "truant_smart":
                    vis = round(random.uniform(80, 92), 1)
                    aud = round(random.uniform(75, 88), 1)
                    beh = round(random.uniform(80, 90), 1)
                elif archetype == "critical":
                    vis = round(random.uniform(30, 52), 1)
                    aud = round(random.uniform(20, 45), 1)
                    beh = round(random.uniform(25, 50), 1)
                else:
                    vis = round(random.uniform(60, 80), 1)
                    aud = round(random.uniform(50, 75), 1)
                    beh = round(random.uniform(55, 80), 1)

            mei_result = agent.calculate_mei(vis, aud, beh, status=status)
            notes = f"Observation: {archetype.capitalize()} profile behavior."

            record_engagement_batch(sess_id, [{
                "student_id": s_id,
                "visual_score": vis,
                "auditory_score": aud,
                "behavioral_score": beh,
                "composite_mei": mei_result["composite_mei"],
                "engagement_tier": mei_result["tier"],
                "notes": notes
            }])

    return True, f"Successfully seeded {len(SAMPLE_STUDENTS)} students across {len(sessions_list)} sessions."

if __name__ == "__main__":
    success, msg = seed_database()
    print(msg)
