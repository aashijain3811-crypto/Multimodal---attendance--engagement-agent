"""
Database Management Module for Multimodal Attendance & Engagement Agent.
Provides robust SQLite connection management, schema initialization, 
parameterized CRUD operations, and analytical query views.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config import DB_PATH, ATTENDANCE_MANDATORY_THRESHOLD

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Creates a connection to SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    """Initializes tables and indexes if they do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        department TEXT NOT NULL,
        semester TEXT NOT NULL,
        section TEXT DEFAULT 'Section A',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Classroom Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT NOT NULL,
        session_date TEXT NOT NULL,
        session_time TEXT DEFAULT '09:00 AM',
        teacher TEXT DEFAULT 'Prof. Dr. R. Sharma',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Attendance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        face_verified INTEGER DEFAULT 0,
        remarks TEXT,
        marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE(session_id, student_id)
    );
    """)

    # 4. Multimodal Engagement Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        visual_score REAL NOT NULL,
        auditory_score REAL NOT NULL,
        behavioral_score REAL NOT NULL,
        composite_mei REAL NOT NULL,
        engagement_tier TEXT NOT NULL,
        notes TEXT,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE(session_id, student_id)
    );
    """)

    # Indexes for rapid retrieval
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_att_sess_stud ON attendance(session_id, student_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eng_sess_stud ON engagement(session_id, student_id);")

    conn.commit()
    conn.close()

# ----------------- Student CRUD ----------------- #

def add_student(roll_number: str, name: str, email: str, department: str, 
                semester: str, section: str = "Section A") -> Tuple[bool, str]:
    """Adds a new student to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (roll_number, name, email, department, semester, section)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (roll_number.strip().upper(), name.strip(), email.strip(), department, semester, section))
        conn.commit()
        return True, f"Student {name} ({roll_number}) added successfully."
    except sqlite3.IntegrityError:
        return False, f"Roll Number '{roll_number}' already exists in database."
    except Exception as e:
        return False, f"Error adding student: {str(e)}"
    finally:
        conn.close()

def update_student(student_id: int, roll_number: str, name: str, email: str, 
                   department: str, semester: str, section: str) -> Tuple[bool, str]:
    """Updates an existing student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE students 
            SET roll_number = ?, name = ?, email = ?, department = ?, semester = ?, section = ?
            WHERE id = ?
        """, (roll_number.strip().upper(), name.strip(), email.strip(), department, semester, section, student_id))
        conn.commit()
        return True, "Student updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Roll Number '{roll_number}' is already assigned to another student."
    except Exception as e:
        return False, f"Error updating student: {str(e)}"
    finally:
        conn.close()

def delete_student(student_id: int) -> Tuple[bool, str]:
    """Deletes student and associated attendance and engagement records."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return True, "Student and associated historical records deleted successfully."
    except Exception as e:
        return False, f"Error deleting student: {str(e)}"
    finally:
        conn.close()

def get_all_students() -> List[Dict[str, Any]]:
    """Returns list of student dictionaries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY roll_number ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_students_df() -> pd.DataFrame:
    """Returns students dataframe."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY roll_number ASC", conn)
    conn.close()
    return df

# ----------------- Session CRUD ----------------- #

def create_session(course: str, session_date: str, session_time: str = "09:00 AM", 
                   teacher: str = "Prof. Dr. R. Sharma", notes: str = "") -> int:
    """Creates a new session and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (course, session_date, session_time, teacher, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (course, session_date, session_time, teacher, notes))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_all_sessions() -> List[Dict[str, Any]]:
    """Returns all classroom sessions sorted by date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM attendance a WHERE a.session_id = s.id) as total_marked,
               (SELECT COUNT(*) FROM attendance a WHERE a.session_id = s.id AND a.status = 'Present') as present_count
        FROM sessions s 
        ORDER BY s.session_date DESC, s.id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_sessions_df() -> pd.DataFrame:
    """Returns sessions dataframe."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM attendance a WHERE a.session_id = s.id) as total_marked,
               (SELECT COUNT(*) FROM attendance a WHERE a.session_id = s.id AND a.status = 'Present') as present_count
        FROM sessions s 
        ORDER BY s.session_date DESC, s.id DESC
    """, conn)
    conn.close()
    return df

# ----------------- Attendance Operations ----------------- #

def mark_attendance_batch(session_id: int, attendance_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Inserts or updates attendance records in batch.
    attendance_data items: {student_id, status, face_verified, remarks}
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION;")
        for item in attendance_data:
            cursor.execute("""
                INSERT INTO attendance (session_id, student_id, status, face_verified, remarks)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id, student_id) DO UPDATE SET
                    status = excluded.status,
                    face_verified = excluded.face_verified,
                    remarks = excluded.remarks,
                    marked_at = CURRENT_TIMESTAMP
            """, (session_id, item["student_id"], item["status"], item.get("face_verified", 0), item.get("remarks", "")))
        conn.commit()
        return True, f"Successfully logged attendance for {len(attendance_data)} students."
    except Exception as e:
        conn.rollback()
        return False, f"Transaction error during attendance marking: {str(e)}"
    finally:
        conn.close()

def get_session_attendance(session_id: int) -> pd.DataFrame:
    """Returns attendance DataFrame for a specific session."""
    conn = get_connection()
    query = """
    SELECT 
        s.id as student_id,
        s.roll_number,
        s.name,
        s.department,
        COALESCE(a.status, 'Not Marked') as status,
        COALESCE(a.face_verified, 0) as face_verified,
        COALESCE(a.remarks, '') as remarks,
        a.marked_at
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id AND a.session_id = ?
    ORDER BY s.roll_number ASC
    """
    df = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return df

# ----------------- Multimodal Engagement Operations ----------------- #

def record_engagement_batch(session_id: int, engagement_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Inserts or updates multimodal engagement data in batch.
    engagement_data items: {student_id, visual_score, auditory_score, behavioral_score, composite_mei, engagement_tier, notes}
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION;")
        for item in engagement_data:
            cursor.execute("""
                INSERT INTO engagement (
                    session_id, student_id, visual_score, auditory_score, 
                    behavioral_score, composite_mei, engagement_tier, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, student_id) DO UPDATE SET
                    visual_score = excluded.visual_score,
                    auditory_score = excluded.auditory_score,
                    behavioral_score = excluded.behavioral_score,
                    composite_mei = excluded.composite_mei,
                    engagement_tier = excluded.engagement_tier,
                    notes = excluded.notes,
                    evaluated_at = CURRENT_TIMESTAMP
            """, (
                session_id, item["student_id"], item["visual_score"], item["auditory_score"],
                item["behavioral_score"], item["composite_mei"], item["engagement_tier"], item.get("notes", "")
            ))
        conn.commit()
        return True, f"Successfully stored engagement analytics for {len(engagement_data)} records."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to record engagement metrics: {str(e)}"
    finally:
        conn.close()

def get_session_engagement(session_id: int) -> pd.DataFrame:
    """Returns engagement DataFrame for a specific session."""
    conn = get_connection()
    query = """
    SELECT 
        s.id as student_id,
        s.roll_number,
        s.name,
        e.visual_score,
        e.auditory_score,
        e.behavioral_score,
        e.composite_mei,
        e.engagement_tier,
        e.notes
    FROM students s
    JOIN engagement e ON s.id = e.student_id AND e.session_id = ?
    ORDER BY s.roll_number ASC
    """
    df = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return df

# ----------------- Comprehensive Analytics & Summaries ----------------- #

def get_complete_attendance_log() -> pd.DataFrame:
    """Returns master joined attendance log across all sessions."""
    conn = get_connection()
    query = """
    SELECT 
        a.id as record_id,
        ses.session_date,
        ses.course,
        ses.session_time,
        stu.roll_number,
        stu.name as student_name,
        stu.department,
        a.status,
        a.face_verified,
        a.remarks,
        a.marked_at
    FROM attendance a
    JOIN sessions ses ON a.session_id = ses.id
    JOIN students stu ON a.student_id = stu.id
    ORDER BY ses.session_date DESC, stu.roll_number ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_student_analytics_summary() -> pd.DataFrame:
    """
    Computes per-student cumulative stats:
    - Total Sessions Held
    - Present, Absent, Late, Excused counts
    - Effective Attendance %: (Present + 0.5 * Late) / Total Sessions * 100
    - Average Multimodal Engagement Index (MEI)
    - Average Visual, Auditory, Behavioral scores
    - Detention Risk Status (<75%)
    """
    conn = get_connection()
    query = """
    WITH StudentAttendance AS (
        SELECT 
            s.id as student_id,
            s.roll_number,
            s.name,
            s.email,
            s.department,
            s.semester,
            COUNT(a.id) as total_sessions,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) as late_count,
            SUM(CASE WHEN a.status = 'Excused' THEN 1 ELSE 0 END) as excused_count,
            SUM(CASE WHEN a.face_verified = 1 THEN 1 ELSE 0 END) as face_verified_count
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id
    ),
    StudentEngagement AS (
        SELECT 
            student_id,
            COUNT(id) as engagement_entries,
            ROUND(AVG(visual_score), 2) as avg_visual,
            ROUND(AVG(auditory_score), 2) as avg_auditory,
            ROUND(AVG(behavioral_score), 2) as avg_behavioral,
            ROUND(AVG(composite_mei), 2) as avg_mei
        FROM engagement
        GROUP BY student_id
    )
    SELECT 
        sa.student_id,
        sa.roll_number,
        sa.name,
        sa.email,
        sa.department,
        sa.semester,
        sa.total_sessions,
        sa.present_count,
        sa.absent_count,
        sa.late_count,
        sa.excused_count,
        sa.face_verified_count,
        CASE 
            WHEN sa.total_sessions > 0 
            THEN ROUND(((sa.present_count + (0.5 * sa.late_count)) * 100.0) / sa.total_sessions, 2)
            ELSE 0.0 
        END as attendance_percentage,
        COALESCE(se.avg_visual, 0.0) as avg_visual,
        COALESCE(se.avg_auditory, 0.0) as avg_auditory,
        COALESCE(se.avg_behavioral, 0.0) as avg_behavioral,
        COALESCE(se.avg_mei, 0.0) as avg_mei,
        CASE 
            WHEN sa.total_sessions > 0 AND (((sa.present_count + (0.5 * sa.late_count)) * 100.0) / sa.total_sessions) < 75.0 
            THEN 1 ELSE 0 
        END as is_at_risk
    FROM StudentAttendance sa
    LEFT JOIN StudentEngagement se ON sa.student_id = se.student_id
    ORDER BY sa.roll_number ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_overall_kpis() -> Dict[str, Any]:
    """Calculates top-level KPI metrics for application dashboard."""
    summary_df = get_student_analytics_summary()
    sessions_df = get_sessions_df()

    total_students = len(summary_df)
    total_sessions = len(sessions_df)

    if total_students == 0 or total_sessions == 0:
        return {
            "total_students": total_students,
            "total_sessions": total_sessions,
            "overall_attendance_rate": 0.0,
            "avg_class_mei": 0.0,
            "at_risk_count": 0,
            "exemplary_count": 0
        }

    overall_attendance_rate = round(summary_df["attendance_percentage"].mean(), 2)
    avg_class_mei = round(summary_df[summary_df["avg_mei"] > 0]["avg_mei"].mean(), 2) if not summary_df.empty else 0.0
    if pd.isna(avg_class_mei):
        avg_class_mei = 0.0

    at_risk_count = int(summary_df["is_at_risk"].sum())
    exemplary_count = int((summary_df["avg_mei"] >= 80.0).sum())

    return {
        "total_students": total_students,
        "total_sessions": total_sessions,
        "overall_attendance_rate": overall_attendance_rate,
        "avg_class_mei": avg_class_mei,
        "at_risk_count": at_risk_count,
        "exemplary_count": exemplary_count
    }

def get_student_dossier(student_id: int) -> Dict[str, Any]:
    """Retrieves full detailed dossier for an individual student."""
    conn = get_connection()
    # 1. Student metadata
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        return {}
    student_info = dict(student_row)

    # 2. Session-by-session attendance & engagement history
    history_query = """
    SELECT 
        s.id as session_id,
        s.session_date,
        s.course,
        COALESCE(a.status, 'Absent') as status,
        COALESCE(a.face_verified, 0) as face_verified,
        COALESCE(a.remarks, '') as remarks,
        e.visual_score,
        e.auditory_score,
        e.behavioral_score,
        e.composite_mei,
        e.engagement_tier
    FROM sessions s
    LEFT JOIN attendance a ON s.id = a.session_id AND a.student_id = ?
    LEFT JOIN engagement e ON s.id = e.session_id AND e.student_id = ?
    ORDER BY s.session_date ASC
    """
    history_df = pd.read_sql_query(history_query, conn, params=(student_id, student_id))
    conn.close()

    total_sessions = len(history_df)
    present_count = int((history_df["status"] == "Present").sum())
    late_count = int((history_df["status"] == "Late").sum())
    absent_count = int((history_df["status"] == "Absent").sum())
    excused_count = int((history_df["status"] == "Excused").sum())

    att_pct = round(((present_count + 0.5 * late_count) / total_sessions * 100), 2) if total_sessions > 0 else 0.0

    valid_mei = history_df["composite_mei"].dropna()
    avg_mei = round(valid_mei.mean(), 2) if not valid_mei.empty else 0.0

    return {
        "student": student_info,
        "history_df": history_df,
        "total_sessions": total_sessions,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
        "excused_count": excused_count,
        "attendance_percentage": att_pct,
        "avg_mei": avg_mei,
        "is_at_risk": att_pct < ATTENDANCE_MANDATORY_THRESHOLD and total_sessions > 0
    }

def reset_database():
    """Drops and recreates all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS engagement;")
    cursor.execute("DROP TABLE IF EXISTS attendance;")
    cursor.execute("DROP TABLE IF EXISTS sessions;")
    cursor.execute("DROP TABLE IF EXISTS students;")
    conn.commit()
    conn.close()
    init_db()
