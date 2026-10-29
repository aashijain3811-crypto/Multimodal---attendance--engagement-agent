"""
Configuration file for Multimodal Attendance & Engagement Agent.
Contains constants, application settings, visual themes, and scoring weights.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.path.join(BASE_DIR, "attendance_agent.db")

# Application Metadata
APP_TITLE = "Multimodal Attendance & Engagement Agent"
APP_SUBTITLE = "AI-Driven Academic Monitoring, Multimodal Analytics & Early Warning System"
APP_VERSION = "2.1.0"
ACADEMIC_YEAR = "2025-2026"
DEFAULT_DEPARTMENT = "Computer Science & Engineering"

# Departments & Courses
DEPARTMENTS = [
    "Computer Science & Engineering",
    "Artificial Intelligence & Machine Learning",
    "Data Science",
    "Information Technology",
    "Electronics & Communication"
]

COURSES = [
    "CS401: Deep Learning & Neural Networks",
    "CS402: Natural Language Processing",
    "CS301: Database Management Systems",
    "CS302: Design & Analysis of Algorithms",
    "AI201: Multimodal Artificial Intelligence",
    "SE305: Software Engineering & Agile Methods"
]

SEMESTERS = ["Semester 1", "Semester 2", "Semester 3", "Semester 4", 
             "Semester 5", "Semester 6", "Semester 7", "Semester 8"]

SECTIONS = ["Section A", "Section B", "Section C"]

# Attendance Statuses
STATUS_PRESENT = "Present"
STATUS_ABSENT = "Absent"
STATUS_LATE = "Late"
STATUS_EXCUSED = "Excused"

ATTENDANCE_STATUSES = [STATUS_PRESENT, STATUS_ABSENT, STATUS_LATE, STATUS_EXCUSED]

# Attendance Status Colors (Hex)
STATUS_COLORS = {
    STATUS_PRESENT: "#10B981",  # Emerald Green
    STATUS_ABSENT: "#EF4444",   # Crimson Red
    STATUS_LATE: "#F59E0B",     # Amber Yellow
    STATUS_EXCUSED: "#6B7280"   # Neutral Gray
}

# University Attendance Regulations
ATTENDANCE_MANDATORY_THRESHOLD = 75.0  # Percentage required to be eligible for end-term exams
ATTENDANCE_WARNING_THRESHOLD = 80.0    # Percentage triggering early advisory

# Multimodal Engagement Weights (Must sum to 1.0)
DEFAULT_ENGAGEMENT_WEIGHTS = {
    "visual": 0.30,      # Eye gaze, screen focus, face orientation
    "auditory": 0.25,    # Verbal questions, class discussion, spoken clarity
    "behavioral": 0.30,  # Quiz responses, note-taking, exercise completion
    "temporal": 0.15     # Punctuality & attendance regularity
}

# Engagement Tiers & Thresholds
ENGAGEMENT_TIERS = {
    "Exemplary": {"min": 80.0, "max": 100.0, "color": "#10B981", "badge": "🟢 Exemplary"},
    "Active": {"min": 65.0, "max": 79.99, "color": "#3B82F6", "badge": "🔵 Active"},
    "Moderate": {"min": 50.0, "max": 64.99, "color": "#F59E0B", "badge": "🟡 Moderate"},
    "Critical": {"min": 0.0, "max": 49.99, "color": "#EF4444", "badge": "🔴 Critical"}
}

# Custom Streamlit UI CSS
CUSTOM_CSS = """
<style>
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 244, 248, 0.95));
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }
    
    /* Modern Section Header */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        border-left: 4px solid #4F46E5;
        padding-left: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Badge Pills */
    .badge-present {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-absent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-late {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-risk {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #F87171;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 600;
    }
    .badge-safe {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
"""
