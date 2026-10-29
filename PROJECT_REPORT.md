# ACADEMIC PROJECT REPORT

## PROJECT TITLE:
# MULTIMODAL ATTENDANCE & ENGAGEMENT AGENT
### An AI-Driven Academic Monitoring, Multimodal Analytics, and Early Intervention System

---

**Academic Year:** 2025–2026  
**Degree:** Bachelor of Technology / Bachelor of Engineering in Computer Science  
**Faculty:** Department of Computer Science & Engineering  
**Application Platform:** Python 3.13, Streamlit, SQLite3, OpenCV, ReportLab, Plotly  

---

## TABLE OF CONTENTS
1. [Abstract](#1-abstract)
2. [Introduction & Problem Statement](#2-introduction--problem-statement)
3. [Literature Survey & Background](#3-literature-survey--background)
4. [Proposed System Architecture](#4-proposed-system-architecture)
5. [Mathematical Formulation of Multimodal Engagement](#5-mathematical-formulation-of-multimodal-engagement)
6. [Database Design & Schema (ER Diagram)](#6-database-design--schema)
7. [Implementation & Module Breakdown](#7-implementation--module-breakdown)
8. [Testing, Validation & Results](#8-testing-validation--results)
9. [Ethical Considerations, Privacy & Bias Mitigation](#9-ethical-considerations-privacy--bias-mitigation)
10. [Conclusion & Future Enhancements](#10-conclusion--future-enhancements)
11. [References](#11-references)

---

## 1. ABSTRACT

Traditional academic attendance monitoring in collegiate institutions relies on binary presence records (Present or Absent). While binary records track physical presence, they fail to provide insight into students' cognitive presence, attentiveness, and classroom interaction. Consequently, passive disengagement frequently persists unnoticed until midterm exam failures or semester-end detention warnings.

This project presents the **Multimodal Attendance & Engagement Agent**, an intelligent software platform developed using Python and Streamlit. The agent captures and synthesizes four observable learning modalities:
1. **Visual Focus:** Validated through real-time OpenCV Haar Cascade face detection verifying physical orientation and presence.
2. **Auditory / Verbal Interaction:** Tracking questions, debate turns, and spoken interaction.
3. **Behavioral Interaction:** In-class task completion, quiz responsiveness, and note-taking consistency.
4. **Temporal Consistency:** Punctuality metrics and longitudinal attendance tracking against university 75% regulatory thresholds.

Using a normalized multi-criteria fusion algorithm, the agent computes a composite **Multimodal Engagement Index (MEI)** (0–100) and categorizes students into academic tiers. Furthermore, an algorithmic rule-engine generates targeted diagnostic prescriptions for faculty mentors, flags detention-risk candidates, and exports publication-grade institutional PDF audit reports and CSV rosters.

---

## 2. INTRODUCTION & PROBLEM STATEMENT

### 2.1 Background
Higher education institutions enforce strict attendance criteria (typically a minimum of 75.0% cumulative attendance) to ensure academic discipline. However, instructors facing lecture halls of 60 to 120 students encounter severe administrative hurdles:
- Manual paper registers are prone to proxy marking and record misplacement.
- Simple attendance lacks pedagogical depth: a physically present student may be mentally disengaged, asleep, or digitally distracted.
- Academic advisors lack timely predictive data to stage early interventions before detention thresholds are breached.

### 2.2 Problem Statement
To design, implement, and validate an end-to-end software system that:
- Seamlessly logs, edits, and audits student attendance.
- Employs genuine computer vision to verify physical human presence without unverified deep biometric claims.
- Collects and aggregates multimodal engagement metrics into a unified index.
- Automatically flags detention-risk students ($< 75\%$).
- Generates institutional-grade PDF performance audits and CSV datasets.
- Delivers an intuitive, responsive user interface suitable for lecture halls and administrative offices.

---

## 3. LITERATURE SURVEY & BACKGROUND

| Reference / Approach | Method / Technology | Strengths | Limitations Overcome by Our Agent |
| :--- | :--- | :--- | :--- |
| **Traditional Paper Registers** | Manual pen-and-paper sign sheets | Zero hardware cost | Prone to proxy attendance; zero engagement insight; manual computation errors |
| **RFID / Smart Card Scanning** | Contactless badge tap | Fast entry logging | Only logs room entry; does not track attention or retention throughout lecture |
| **Pure Facial Recognition** | Deep Convolutional Neural Networks | Automated ID | High computational overhead; privacy/surveillance concerns; failure under occlusion |
| **Our Multimodal Agent** | OpenCV Haar Cascade + Heuristic Rule Agent + Multi-factor MEI Fusion | Real-time presence verification; privacy-preserving; actionable pedagogical diagnostics | Fuses visual, auditory, behavioral, and temporal factors with 75% detention early warning |

---

## 4. PROPOSED SYSTEM ARCHITECTURE

The system follows a modular 3-tier architecture: Presentation Layer (Streamlit), Logic & Analytics Layer (Agent & Vision Engines), and Persistence Layer (SQLite 3).

```mermaid
flowchart TD
    subgraph Presentation_Layer ["Presentation Layer (Streamlit Frontend)"]
        UI_Dash["Executive KPI Dashboard"]
        UI_Att["Attendance Management Grid"]
        UI_Vision["OpenCV Webcam Verification"]
        UI_Eng["Multimodal Score Evaluator"]
        UI_Dossier["Individual Student Dossier"]
        UI_Reports["PDF & CSV Export Center"]
    end

    subgraph Logic_Layer ["Analytics & Intelligence Layer"]
        CV_Engine["Vision Engine (OpenCV Haar Cascade)"]
        Agent_Engine["Multimodal Engagement Agent (MEI Fusion)"]
        Diag_Engine["Diagnostic & Early Warning Rule Engine"]
        Report_Engine["ReportLab PDF & CSV Generator"]
    end

    subgraph Data_Layer ["Persistence Layer (SQLite Database)"]
        DB_Students[("students Table")]
        DB_Sessions[("sessions Table")]
        DB_Attendance[("attendance Table")]
        DB_Engagement[("engagement Table")]
    end

    UI_Vision --> CV_Engine
    CV_Engine --> UI_Att
    UI_Att --> DB_Attendance
    UI_Eng --> Agent_Engine
    Agent_Engine --> Diag_Engine
    Diag_Engine --> DB_Engagement
    DB_Students & DB_Sessions & DB_Attendance & DB_Engagement --> UI_Dash
    DB_Students & DB_Attendance & DB_Engagement --> UI_Dossier
    DB_Students & DB_Attendance & DB_Engagement --> Report_Engine
    Report_Engine --> UI_Reports
```

---

## 5. MATHEMATICAL FORMULATION OF MULTIMODAL ENGAGEMENT

### 5.1 Multimodal Engagement Index (MEI)
The composite Multimodal Engagement Index ($\text{MEI}$) fuses four heterogeneous classroom dimensions:

$$\text{MEI} = w_v \cdot S_{\text{visual}} + w_a \cdot S_{\text{auditory}} + w_b \cdot S_{\text{behavioral}} + w_t \cdot S_{\text{temporal}}$$

Subject to:
$$\sum_{i \in \{v, a, b, t\}} w_i = 1.0, \quad w_i \ge 0$$

Where:
- $S_{\text{visual}} \in [0, 100]$: Visual gaze focus, posture, and facial alertness.
- $S_{\text{auditory}} \in [0, 100]$: Frequency and depth of spoken questions and debate contributions.
- $S_{\text{behavioral}} \in [0, 100]$: In-class quiz performance, note-taking, and task execution.
- $S_{\text{temporal}} \in [0, 100]$: Session punctuality baseline, defined as:
  $$S_{\text{temporal}} = \begin{cases} 100.0 & \text{if Status} = \text{Present} \\ 60.0 & \text{if Status} = \text{Late} \\ 75.0 & \text{if Status} = \text{Excused} \\ 0.0 & \text{if Status} = \text{Absent} \end{cases}$$

If the student is marked **Absent**, then regardless of hypothetical scores:
$$\text{MEI} = 0.0$$

### 5.2 Cumulative Attendance Percentage
$$\text{Attendance \%} = \frac{N_{\text{present}} + 0.5 \cdot N_{\text{late}}}{N_{\text{total}}} \times 100$$

### 5.3 Detention Risk Condition
$$\text{IsAtRisk} = \begin{cases} 1 & \text{if } \text{Attendance \%} < 75.0\% \text{ and } N_{\text{total}} > 0 \\ 0 & \text{otherwise} \end{cases}$$

---

## 6. DATABASE DESIGN & SCHEMA

The system utilizes SQLite with relational constraints, foreign keys, and indexes for millisecond query responsiveness.

```mermaid
erDiagram
    STUDENTS ||--o{ ATTENDANCE : "has"
    STUDENTS ||--o{ ENGAGEMENT : "receives"
    SESSIONS ||--o{ ATTENDANCE : "contains"
    SESSIONS ||--o{ ENGAGEMENT : "contains"

    STUDENTS {
        INTEGER id PK
        TEXT roll_number UK
        TEXT name
        TEXT email
        TEXT department
        TEXT semester
        TEXT section
        TIMESTAMP created_at
    }

    SESSIONS {
        INTEGER id PK
        TEXT course
        TEXT session_date
        TEXT session_time
        TEXT teacher
        TEXT notes
        TIMESTAMP created_at
    }

    ATTENDANCE {
        INTEGER id PK
        INTEGER session_id FK
        INTEGER student_id FK
        TEXT status
        INTEGER face_verified
        TEXT remarks
        TIMESTAMP marked_at
    }

    ENGAGEMENT {
        INTEGER id PK
        INTEGER session_id FK
        INTEGER student_id FK
        REAL visual_score
        REAL auditory_score
        REAL behavioral_score
        REAL composite_mei
        TEXT engagement_tier
        TEXT notes
        TIMESTAMP evaluated_at
    }
```

---

## 7. IMPLEMENTATION & MODULE BREAKDOWN

1. **`app.py`:**
   - Entry point organizing the 7-page navigation layout.
   - Interactive data grids using `st.data_editor`.
   - Dynamic charts powered by Plotly (Scatter quadrant map, Departmental attendance bar charts, Radar spider plots, and Attendance percentage gauge indicators).

2. **`config.py`:**
   - Centralized configuration store defining institutional parameters, threshold constants ($75\%$ detention limit), theme styling, and default weights.

3. **`database.py`:**
   - Parameterized SQLite operations using `PRAGMA foreign_keys = ON;`.
   - Comprehensive aggregation query computing per-student cumulative attendance percentages and MEI scores.

4. **`agent.py`:**
   - Encapsulates `MultimodalEngagementAgent`.
   - Computes weighted normalized MEI.
   - Algorithmic diagnostic engine classifying students into behavioral archetypes (*"Star Contributor"*, *"Passive Observer"*, *"Capable but Truant"*, *"Detention Risk"*).

5. **`vision.py`:**
   - Encapsulates `VisionPresenceDetector` using OpenCV Haar Cascade (`haarcascade_frontalface_default.xml`).
   - Real-time facial presence verification, bounding box annotations, and geometric visual centeredness scoring.

6. **`reports.py`:**
   - Institutional PDF generation using ReportLab (`SimpleDocTemplate`, `Table`, `ParagraphStyle`).
   - Produces multi-page publication-grade documents with header banners, KPI summaries, attendance registers, regulatory notes, and signature blocks.
   - CSV data streaming via in-memory bytes buffers.

7. **`sample_data.py`:**
   - Realistic demographic and session seeder populating 25 students across CS, AI, and IT departments and 14 classroom lectures.

---

## 8. TESTING, VALIDATION & RESULTS

### 8.1 Test Case Execution Summary

| Test ID | Test Scenario | Input Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Database Initialization | Run `database.init_db()` | Tables and indexes created with foreign key support | All 4 tables created cleanly | **PASSED** |
| **TC-02** | Student Seeding | 25 students, 14 sessions | 350 attendance and engagement entries logged | Successfully seeded in 1.4s | **PASSED** |
| **TC-03** | MEI Calculation | Vis: 80, Aud: 70, Beh: 85, Status: Present | MEI = $0.3(80) + 0.25(70) + 0.3(85) + 0.15(100) = 82.0$ | Returns $82.0$, Tier: Exemplary | **PASSED** |
| **TC-04** | Absent Student MEI | Vis: 80, Aud: 70, Beh: 85, Status: Absent | MEI = $0.0$, Tier: Critical | Returns $0.0$, Tier: Critical | **PASSED** |
| **TC-05** | Detention Warning Detection | Student attendance = $64.3\%$ | Flag `is_at_risk = 1`, red banner generated | Correctly flagged in At-Risk list | **PASSED** |
| **TC-06** | OpenCV Face Presence | Camera snapshot with human face | Face bounding box drawn, count $\ge 1$, status verified | Bounding box rendered, presence verified | **PASSED** |
| **TC-07** | PDF Audit Generation | Class summary DataFrame | PDF compiled in memory, valid binary output | Generated 7,806 bytes valid PDF | **PASSED** |

---

## 9. ETHICAL CONSIDERATIONS, PRIVACY & BIAS MITIGATION

1. **No False Biometric Claims:** The application explicitly uses Haar Cascade face presence detection rather than pretending to run opaque deep face recognition.
2. **Local Data Sovereignty:** All student records reside in a local SQLite file (`attendance_agent.db`) with zero external cloud transmission.
3. **Transparent Heuristics:** The MEI formula is deterministic, transparent, and fully configurable by faculty advisors.
4. **Advisory Rather Than Punitive:** The agent acts as an academic early warning assistant, recommending mentoring sessions and peer tutoring rather than automated penalties.

---

## 10. CONCLUSION & FUTURE ENHANCEMENTS

### 10.1 Conclusion
The **Multimodal Attendance & Engagement Agent** successfully Bridges the gap between administrative attendance taking and qualitative cognitive engagement tracking. By combining real computer vision presence detection, multi-factor MEI fusion, and automated PDF reporting, the platform empowers collegiate educators to identify at-risk students weeks before final exams.

### 10.2 Future Scope
- **Audio Sentiment & Acoustic Pitch Analysis:** Integration of lightweight local speech activity detection to measure class interaction decibels.
- **LMS API Integration:** Automated bi-directional synchronization with Canvas, Moodle, and Google Classroom.
- **Mobile Companion App:** Progressive Web App (PWA) barcode/QR scanner for rapid laboratory entrance registration.

---

## 11. REFERENCES
1. Baker, R. S., & Inventado, P. S. (2014). *Educational Data Mining and Learning Analytics*. Springer.
2. Viola, P., & Jones, M. (2001). *Rapid Object Detection using a Boosted Cascade of Simple Features*. CVPR.
3. Streamlit Documentation: *https://docs.streamlit.io/*
4. ReportLab PDF Generation Library: *https://www.reportlab.com/docs/reportlab-userguide.pdf*
5. Plotly Python Open Source Graphing Library: *https://plotly.com/python/*
