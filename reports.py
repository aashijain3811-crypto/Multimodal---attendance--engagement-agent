"""
Report Generation Module for Multimodal Attendance & Engagement Agent.
Provides CSV data export and professional institutional PDF report generation
using ReportLab with clean typography, styled KPI tables, and formal academic signatures.
"""

import io
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_csv_bytes(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to UTF-8 encoded CSV bytes."""
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8")
    return output.getvalue().encode("utf-8")

def generate_pdf_report(
    summary_df: pd.DataFrame, 
    kpis: Dict[str, Any], 
    course_name: str = "All Courses",
    academic_term: str = "Academic Year 2025-2026"
) -> bytes:
    """
    Builds a multi-page, publication-grade academic performance and attendance PDF report.
    Returns in-memory PDF binary bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_LEFT
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#312E81'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    body_center = ParagraphStyle(
        'BodyCenter',
        parent=body_style,
        alignment=TA_CENTER
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    elements = []

    # 1. Document Header
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    header_data = [
        [
            Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</b><br/><font size='14'><b>Multimodal Attendance & Engagement Agent - Official Academic Audit</b></font>", title_style),
            Paragraph(f"<b>Generated:</b> {now_str}<br/><b>Term:</b> {academic_term}<br/><b>Filter:</b> {course_name}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[520, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=12, spaceBefore=6))

    # 2. Executive KPI Cards Table
    kpi_data = [
        [
            Paragraph("<b>Total Enrolled</b>", body_center),
            Paragraph("<b>Overall Attendance</b>", body_center),
            Paragraph("<b>Average MEI Score</b>", body_center),
            Paragraph("<b>Detention Risk (<75%)</b>", body_center),
            Paragraph("<b>Exemplary Scholars</b>", body_center),
        ],
        [
            Paragraph(f"<font size='14'><b>{kpis.get('total_students', 0)}</b></font>", body_center),
            Paragraph(f"<font size='14'><b>{kpis.get('overall_attendance_rate', 0.0)}%</b></font>", body_center),
            Paragraph(f"<font size='14'><b>{kpis.get('avg_class_mei', 0.0)}/100</b></font>", body_center),
            Paragraph(f"<font size='14' color='#DC2626'><b>{kpis.get('at_risk_count', 0)}</b></font>", body_center),
            Paragraph(f"<font size='14' color='#16A34A'><b>{kpis.get('exemplary_count', 0)}</b></font>", body_center),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[144, 144, 144, 144, 144])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # 3. Student Roster Table
    elements.append(Paragraph("<b>STUDENT PERFORMANCE & ATTENDANCE REGISTER</b>", section_heading))

    # Build student rows
    headers = ["Roll Number", "Student Name", "Department", "Sessions", "Present", "Absent", "Late", "Att %", "Avg MEI", "Status"]
    table_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

    for idx, row in summary_df.iterrows():
        att_val = row.get("attendance_percentage", 0.0)
        mei_val = row.get("avg_mei", 0.0)
        is_risk = row.get("is_at_risk", 0) == 1

        status_text = "<font color='#DC2626'><b>AT-RISK</b></font>" if is_risk else "<font color='#16A34A'><b>NORMAL</b></font>"
        att_color = "#DC2626" if is_risk else "#16A34A"

        row_cells = [
            Paragraph(str(row.get("roll_number", "")), body_style),
            Paragraph(str(row.get("name", "")), body_style),
            Paragraph(str(row.get("department", "")).replace("Engineering", "Engg"), body_style),
            Paragraph(str(row.get("total_sessions", 0)), body_center),
            Paragraph(str(row.get("present_count", 0)), body_center),
            Paragraph(str(row.get("absent_count", 0)), body_center),
            Paragraph(str(row.get("late_count", 0)), body_center),
            Paragraph(f"<font color='{att_color}'><b>{att_val:.1f}%</b></font>", body_center),
            Paragraph(f"<b>{mei_val:.1f}</b>", body_center),
            Paragraph(status_text, body_center)
        ]
        table_rows.append(row_cells)

    # Column widths summing to 720
    roster_table = Table(table_rows, colWidths=[75, 125, 120, 50, 45, 45, 40, 55, 55, 65], repeatRows=1)
    
    # Alternate row colors
    roster_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#312E81')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    for i in range(1, len(table_rows)):
        bg_col = colors.HexColor('#F8FAFC') if i % 2 == 0 else colors.white
        roster_style.append(('BACKGROUND', (0, i), (-1, i), bg_col))

    roster_table.setStyle(TableStyle(roster_style))
    elements.append(roster_table)
    elements.append(Spacer(1, 16))

    # 4. Mandatory Attendance Policy & Signatures
    policy_text = (
        "<b>Institutional Regulatory Compliance:</b> As per University Academic Regulation §14.2, students maintaining "
        "less than 75.0% cumulative classroom attendance are disqualified from appearing in end-semester examinations without formal "
        "condonation approved by the Academic Council. Multimodal Engagement Index (MEI) synthesizes visual, auditory, and behavioral "
        "classroom factors for pedagogical diagnostic purposes."
    )
    elements.append(Paragraph(policy_text, subtitle_style))
    elements.append(Spacer(1, 20))

    # Formal Signature Blocks
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Course Instructor</b><br/>Prof. Dr. R. Sharma", body_center),
            Paragraph("____________________________<br/><b>Head of Department</b><br/>Dept. of CSE", body_center),
            Paragraph("____________________________<br/><b>Dean of Academic Affairs</b><br/>College Academic Council", body_center),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[240, 240, 240])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(sig_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
