# 🎓 Multimodal Attendance & Engagement Agent

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://www.sqlite.org/)
[![Computer Vision](https://img.shields.io/badge/CV-OpenCV%20Haar%20Cascade-5C3EE8.svg)](https://opencv.org/)
[![Reporting](https://img.shields.io/badge/PDF%20Engine-ReportLab-009688.svg)](https://www.reportlab.com/)

An AI-driven academic monitoring, multimodal engagement analytics, and early warning detention risk intervention system built for modern educational institutions.

---

## 🌟 Key Features

1. **Student Attendance Management**
   - Track student attendance by **Roll Number**, **Name**, **Session Date**, and status (`Present`, `Absent`, `Late`, `Excused`).
   - Batch classroom attendance marking grid with single-click shortcuts (`Mark All Present`, `Mark All Absent`).
   - Historical attendance register with multi-criteria filtering (Course, Date Range, Status, Student Search).

2. **Real Computer Vision Visual Presence Verification**
   - **Honest Implementation:** Uses real **OpenCV Haar Cascade Face Detection** (`haarcascade_frontalface_default.xml`) on webcam snapshots or uploaded photos.
   - Draws bounding boxes, counts human faces in frame, validates physical presence, and computes geometric visual focus scores.

3. **Multimodal Engagement Index (MEI)**
   - Computes a mathematically grounded composite engagement score from four observable dimensions:
     - 👁️ **Visual Focus ($S_v$)**: Gaze orientation, visual presence, alertness.
     - 🎙️ **Auditory / Verbal Interaction ($S_a$)**: Spoken questions, debate contributions, vocal response.
     - 📝 **Behavioral / Task Execution ($S_b$)**: Quiz completion, note-taking, exercise punctuality.
     - ⏱️ **Temporal Factor ($S_t$)**: Punctual arrival and attendance consistency.
   - Categorizes students into 4 standardized academic engagement tiers:
     - 🟢 **Exemplary** (MEI $\ge 80$)
     - 🔵 **Active** ($65 \le \text{MEI} < 80$)
     - 🟡 **Moderate** ($50 \le \text{MEI} < 65$)
     - 🔴 **Critical** ($\text{MEI} < 50$)

4. **University Detention Early Warning System**
   - Automatically tracks the mandatory **75.0% University Attendance Threshold**.
   - Flags at-risk students with prominent visual alert cards and generates personalized counseling recommendations.

5. **Student-Wise Dossier & Analytics**
   - Individual student profile cards with attendance percentage gauge charts.
   - Session-by-session historical attendance log and longitudinal MEI progression curves.
   - Algorithmic behavioral archetype diagnosis (e.g. *"Passive Observer"*, *"Capable but Truant"*, *"Star Contributor"*).

6. **Institutional PDF & CSV Reports**
   - **Publication-grade PDF Academic Audit Report** powered by ReportLab (includes executive KPIs, roster tables, detention warnings, and formal signature blocks).
   - **Tabular CSV Exports** for spreadsheet analysis and LMS integration.

7. **Sample Data Generator & Reset**
   - Built-in one-click **"🌱 Load Demo"** button to populate 25 realistic college students, 14 past classroom lectures, and hundreds of attendance and multimodal engagement entries.

---

## 🏗️ System Architecture & File Structure

```
AttendenceAgent/
├── app.py                  # Main Streamlit dashboard application
├── config.py               # Constants, application metadata, styling, and weights
├── database.py             # SQLite database layer: schema, parameterized CRUD, views
├── agent.py                # Multimodal Engagement Agent: MEI fusion & diagnostic engine
├── vision.py               # Computer vision module: OpenCV Haar Cascade face presence
├── reports.py              # Export engine: CSV formatter & styled ReportLab PDF generator
├── sample_data.py          # Realistic college demo dataset generator
├── requirements.txt        # Python package dependencies
├── run.bat                 # One-click Windows runner script
├── README.md               # Setup guide & project overview (this file)
└── PROJECT_REPORT.md       # Comprehensive academic college project report
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- **Python 3.10 or higher** (Python 3.11, 3.12, 3.13 supported).
- Pip package installer.

### 2. Installation

1. Open your terminal or PowerShell in the project directory:
   ```bash
   cd c:\Users\ranua\Downloads\AttendenceAgent
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Windows Command Prompt:
   .\venv\Scripts\activate.bat
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Launching the Application

Run the application using Streamlit:
```bash
streamlit run app.py
```

*Or simply double-click the included `run.bat` file on Windows!*

Once launched, open your web browser to:
```
http://localhost:8501
```

### 4. Exploring the Demo
1. In the sidebar on the left, click **"🌱 Load Demo"**.
2. The application will instantly populate **25 diverse college students**, **14 historical classroom sessions**, and hundreds of attendance and engagement logs.
3. Explore the **Executive Dashboard**, mark batch attendance in **Attendance Management**, test the **OpenCV face detector** in the webcam tab, review individual student dossiers, and click **Download Official PDF Report**!

---

## 📐 Mathematical Formulation of Multimodal Engagement

The composite Multimodal Engagement Index ($\text{MEI}$) is computed via normalized multi-criteria sensor fusion:

$$\text{MEI} = w_v \cdot S_{\text{visual}} + w_a \cdot S_{\text{auditory}} + w_b \cdot S_{\text{behavioral}} + w_t \cdot S_{\text{temporal}}$$

Where:
- $\sum w_i = 1.0$ (Default weights: $w_v = 0.30$, $w_a = 0.25$, $w_b = 0.30$, $w_t = 0.15$)
- $S_{\text{temporal}} = \begin{cases} 100.0 & \text{if Present} \\ 60.0 & \text{if Late} \\ 75.0 & \text{if Excused} \\ 0.0 & \text{if Absent} \end{cases}$
- If $Status = \text{Absent}$, $\text{MEI} = 0.0$.

Cumulative Attendance Percentage:
$$\text{Attendance \%} = \frac{\text{Present Count} + (0.5 \times \text{Late Count})}{\text{Total Sessions Held}} \times 100$$

A student is flagged as **At-Risk** if $\text{Attendance \%} < 75.0\%$.

---

## 🛡️ Honesty & Technical Integrity Statement

In compliance with project specifications:
- **Face Presence Verification:** Implemented using OpenCV's standard Haar Cascade classifier (`haarcascade_frontalface_default.xml`). It detects the physical presence and location of human faces in webcam frames. It **does not claim** deep neural biometric facial recognition identification.
- **Auditory Modality:** Structured quantitative logging of classroom verbal participation and debate turns, rather than claiming unsupported deep voiceprint identification.
- **Agent Intelligence:** Heuristic rule-based expert diagnostic engine that analyzes discrepancies between attendance, visual focus, and verbal participation to prescribe actionable student counseling interventions.

---

## 📖 College Project Documentation

For the complete academic project report including:
- **Chapter 1:** Introduction & Motivation
- **Chapter 2:** Literature Survey & Related Work
- **Chapter 3:** Proposed System Architecture & Flowcharts
- **Chapter 4:** Multimodal Mathematical Modeling
- **Chapter 5:** Database Schema & ER Diagram
- **Chapter 6:** Implementation & Module Walkthrough
- **Chapter 7:** Experimental Results & Evaluation
- **Chapter 8:** Conclusion & Future Scope

Please refer to [`PROJECT_REPORT.md`](file:///c:/Users/ranua/Downloads/AttendenceAgent/PROJECT_REPORT.md).
