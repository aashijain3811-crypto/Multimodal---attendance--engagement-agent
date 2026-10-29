"""
Multimodal Attendance & Engagement Agent - Streamlit Application.
Main entry point featuring modern dashboard layout, interactive charts,
batch attendance management, real computer vision presence detection,
AI agent analytics, and PDF/CSV reporting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

# Import project modules
import config
import database
from agent import MultimodalEngagementAgent
from vision import detector
import reports
import sample_data

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom modern styling
st.markdown(config.CUSTOM_CSS, unsafe_allow_html=True)

# Initialize database schema
database.init_db()

# Initialize session state variables
if "agent_weights" not in st.session_state:
    st.session_state.agent_weights = config.DEFAULT_ENGAGEMENT_WEIGHTS.copy()

agent = MultimodalEngagementAgent(weights=st.session_state.agent_weights)

# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 **Attendance & Engagement**")
    st.caption("Multimodal Academic Monitoring Agent")
    st.markdown("---")

    # Navigation menu
    selected_page = st.radio(
        "Navigation Menu",
        [
            "📊 Executive Dashboard",
            "📝 Attendance Management",
            "🧠 Multimodal Engagement Agent",
            "👤 Student Dossier & Analytics",
            "📑 Reports & Downloads",
            "👥 Student & Session Directory",
            "⚙️ Settings & Project Overview"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("##### ⚡ Quick Demonstration")
    col_seed1, col_seed2 = st.columns(2)
    with col_seed1:
        if st.button("🌱 Load Demo", use_container_width=True, help="Populate 25 students and multi-week lecture records"):
            with st.spinner("Seeding database..."):
                sample_data.seed_database()
                st.toast("✅ Demo data successfully loaded!", icon="🚀")
                st.rerun()

    with col_seed2:
        if st.button("🔄 Reset DB", use_container_width=True, help="Wipe all data for clean start"):
            database.reset_database()
            st.toast("Database reset to blank state.", icon="🧹")
            st.rerun()

    st.markdown("---")
    st.caption(f"**Version:** {config.APP_VERSION}")
    st.caption("College Capstone Project • 2026")

# Check if database has students
all_students_df = database.get_students_df()
has_data = len(all_students_df) > 0

# -------------------------------------------------------------
# PAGE 1: EXECUTIVE DASHBOARD
# -------------------------------------------------------------
if selected_page == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard & Analytics")
    st.markdown(f"*{config.APP_SUBTITLE}*")

    if not has_data:
        st.info("👋 Welcome! The database is currently empty. Click **'🌱 Load Demo'** in the left sidebar to populate realistic classroom data for an immediate interactive tour.")
    else:
        kpis = database.get_overall_kpis()
        summary_df = database.get_student_analytics_summary()

        # Top Metric Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Enrolled", f"{kpis['total_students']}", "Active Students")
        with col2:
            st.metric("Sessions Held", f"{kpis['total_sessions']}", "Lectures")
        with col3:
            att_delta = f"{'+' if kpis['overall_attendance_rate'] >= 75 else ''}{kpis['overall_attendance_rate'] - 75:.1f}% vs 75% Min"
            st.metric("Overall Attendance", f"{kpis['overall_attendance_rate']}%", att_delta)
        with col4:
            st.metric("Avg Class MEI", f"{kpis['avg_class_mei']}/100", "Multimodal Score")
        with col5:
            st.metric("At-Risk (<75%)", f"{kpis['at_risk_count']}", "Detention Danger", delta_color="inverse")

        st.markdown("---")

        # Early Warning Alert Banner
        at_risk_df = summary_df[summary_df["is_at_risk"] == 1]
        if not at_risk_df.empty:
            with st.expander(f"⚠️ **Early Warning Notice: {len(at_risk_df)} Student(s) Below 75% Attendance Threshold**", expanded=True):
                st.markdown(
                    "According to university academic regulations, students with cumulative attendance under 75% "
                    "are ineligible for semester-end examinations without formal approved condonation."
                )
                cols_to_show = ["roll_number", "name", "department", "total_sessions", "present_count", "attendance_percentage", "avg_mei"]
                display_risk = at_risk_df[cols_to_show].rename(columns={
                    "roll_number": "Roll No",
                    "name": "Student Name",
                    "department": "Department",
                    "total_sessions": "Lectures",
                    "present_count": "Attended",
                    "attendance_percentage": "Attendance %",
                    "avg_mei": "Avg MEI"
                })
                st.dataframe(
                    display_risk.style.format({"Attendance %": "{:.1f}%", "Avg MEI": "{:.1f}"})
                    .background_gradient(subset=["Attendance %"], cmap="Reds_r"),
                    use_container_width=True
                )

        # Charts Section
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.subheader("📈 Attendance vs Engagement Correlation")
            st.caption("Visualizes student distribution across Attendance % and Multimodal Engagement Index (MEI)")
            
            fig_scatter = px.scatter(
                summary_df,
                x="attendance_percentage",
                y="avg_mei",
                hover_name="name",
                hover_data={"roll_number": True, "department": True, "attendance_percentage": True, "avg_mei": True},
                color="department",
                size=[18] * len(summary_df),
                labels={"attendance_percentage": "Attendance Rate (%)", "avg_mei": "Multimodal Engagement Index (MEI)"},
                title="Student Academic Quadrant Map"
            )
            # Add threshold guide lines
            fig_scatter.add_vline(x=75, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text="75% Min Attendance", annotation_position="top left")
            fig_scatter.add_hline(y=65, line_width=2, line_dash="dot", line_color="#F59E0B", annotation_text="65 MEI Baseline", annotation_position="bottom right")
            fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380, legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_scatter, use_container_width=True)

        with c_right:
            st.subheader("📊 Attendance Distribution by Department")
            st.caption("Comparative departmental attendance performance")
            
            dept_stats = summary_df.groupby("department")["attendance_percentage"].mean().reset_index()
            fig_bar = px.bar(
                dept_stats,
                x="department",
                y="attendance_percentage",
                color="attendance_percentage",
                color_continuous_scale="Viridis",
                labels={"department": "Academic Department", "attendance_percentage": "Avg Attendance (%)"},
                text_auto=".1f",
                title="Departmental Average Attendance Rate"
            )
            fig_bar.add_hline(y=75, line_dash="dash", line_color="red")
            fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Bottom Row: Multimodal Breakdown & Digest
        b_left, b_right = st.columns([1, 1])
        with b_left:
            st.subheader("🕸️ Class-wide Multimodal Component Balance")
            st.caption("Average scores across the four tracked learning modalities")
            
            avg_vis = summary_df["avg_visual"].mean() if not summary_df.empty else 0
            avg_aud = summary_df["avg_auditory"].mean() if not summary_df.empty else 0
            avg_beh = summary_df["avg_behavioral"].mean() if not summary_df.empty else 0
            avg_att = summary_df["attendance_percentage"].mean() if not summary_df.empty else 0

            radar_df = pd.DataFrame(dict(
                r=[avg_vis, avg_aud, avg_beh, avg_att],
                theta=['Visual Focus', 'Auditory Participation', 'Behavioral Task', 'Punctuality/Attendance']
            ))
            fig_radar = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
            fig_radar.update_traces(fill='toself', fillcolor='rgba(79, 70, 229, 0.35)', line=dict(color='#4F46E5', width=3))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                margin=dict(l=40, r=40, t=20, b=20),
                height=320
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with b_right:
            st.subheader("💡 Intelligent Agent Actionable Digest")
            st.caption("Heuristic synthesis generated by the Multimodal Agent")
            
            digest = agent.generate_classroom_digest(summary_df)
            st.markdown("##### 🚨 Critical Observations")
            for alert in digest["alerts"]:
                st.markdown(f"- {alert}")
            
            st.markdown("##### 🎯 Suggested Pedagogical Interventions")
            for sug in digest["suggestions"]:
                st.markdown(f"- {sug}")

# -------------------------------------------------------------
# PAGE 2: ATTENDANCE MANAGEMENT
# -------------------------------------------------------------
elif selected_page == "📝 Attendance Management":
    st.title("📝 Student Attendance Management")
    st.markdown("Record, edit, verify with real computer vision, and audit attendance records.")

    if not has_data:
        st.warning("⚠️ No students registered yet. Please add students in 'Student & Session Directory' or load sample demo data.")
    else:
        sessions_df = database.get_sessions_df()
        
        tab_batch, tab_single, tab_vision, tab_history = st.tabs([
            "📋 Batch Session Attendance",
            "👤 Quick Single Entry",
            "📷 Real Visual Presence Verification",
            "📜 Full Attendance Register & Audit"
        ])

        # TAB 1: BATCH SESSION ATTENDANCE
        with tab_batch:
            st.subheader("Classroom Session Attendance Register")
            
            # Select or create session
            if sessions_df.empty:
                st.info("No classroom sessions exist yet. Create your first session below:")
                with st.form("create_first_session"):
                    c_course = st.selectbox("Course / Subject", config.COURSES)
                    c_date = st.date_input("Session Date", value=date.today())
                    c_time = st.selectbox("Time Slot", ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "02:00 PM - 03:00 PM"])
                    c_teacher = st.text_input("Instructor", "Prof. Dr. R. Sharma")
                    if st.form_submit_button("Create Session & Start"):
                        new_id = database.create_session(c_course, str(c_date), c_time, c_teacher)
                        st.success(f"Session #{new_id} created!")
                        st.rerun()
            else:
                session_options = {
                    f"#{row['id']} | {row['session_date']} | {row['course']} ({row['session_time']})": row['id']
                    for _, row in sessions_df.iterrows()
                }
                
                col_s1, col_s2 = st.columns([3, 1])
                with col_s1:
                    chosen_label = st.selectbox("Select Lecture Session to Mark / Edit", list(session_options.keys()))
                    chosen_session_id = session_options[chosen_label]
                with col_s2:
                    st.write("")
                    st.write("")
                    if st.button("➕ New Session", help="Add a new lecture session"):
                        st.session_state.show_new_session_dialog = True

                # Current session attendance table
                curr_att_df = database.get_session_attendance(chosen_session_id)
                
                st.markdown(f"**Marking Attendance for Session #{chosen_session_id}** ({len(curr_att_df)} Students)")

                # Quick action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                with col_btn1:
                    mark_all_p = st.button("✅ Mark All Present", help="Set status of all students to Present")
                with col_btn2:
                    mark_all_a = st.button("❌ Mark All Absent", help="Set status of all students to Absent")

                # Editable grid
                editable_data = []
                for _, s_row in curr_att_df.iterrows():
                    default_status = s_row["status"]
                    if default_status == "Not Marked":
                        default_status = "Present"
                    if mark_all_p:
                        default_status = "Present"
                    elif mark_all_a:
                        default_status = "Absent"

                    editable_data.append({
                        "student_id": s_row["student_id"],
                        "Roll Number": s_row["roll_number"],
                        "Student Name": s_row["name"],
                        "Department": s_row["department"],
                        "Status": default_status,
                        "Remarks": s_row["remarks"] if s_row["remarks"] else ""
                    })

                grid_df = pd.DataFrame(editable_data)
                
                edited_df = st.data_editor(
                    grid_df,
                    column_config={
                        "student_id": None, # Hide internal ID
                        "Roll Number": st.column_config.TextColumn("Roll Number", disabled=True),
                        "Student Name": st.column_config.TextColumn("Student Name", disabled=True),
                        "Department": st.column_config.TextColumn("Department", disabled=True),
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=config.ATTENDANCE_STATUSES,
                            required=True
                        ),
                        "Remarks": st.column_config.TextColumn("Remarks / Notes")
                    },
                    disabled=["student_id", "Roll Number", "Student Name", "Department"],
                    use_container_width=True,
                    num_rows="fixed",
                    key=f"editor_session_{chosen_session_id}"
                )

                if st.button("💾 Save Attendance Records", type="primary", use_container_width=True):
                    batch_payload = []
                    for _, row in edited_df.iterrows():
                        batch_payload.append({
                            "student_id": int(row["student_id"]),
                            "status": row["Status"],
                            "face_verified": 0,
                            "remarks": str(row["Remarks"])
                        })
                    success, msg = database.mark_attendance_batch(chosen_session_id, batch_payload)
                    if success:
                        st.success(f"🎉 {msg}")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")

        # TAB 2: SINGLE ENTRY
        with tab_single:
            st.subheader("Log Individual Student Attendance")
            with st.form("single_att_form"):
                col_in1, col_in2 = st.columns(2)
                with col_in1:
                    student_choices = {f"{s['roll_number']} - {s['name']} ({s['department']})": s['id'] for s in database.get_all_students()}
                    picked_student_str = st.selectbox("Select Student", list(student_choices.keys()))
                    picked_student_id = student_choices[picked_student_str]

                    picked_session_str = st.selectbox("Select Lecture Session", list(session_options.keys()) if not sessions_df.empty else [])
                    picked_session_id = session_options[picked_session_str] if not sessions_df.empty else 1

                with col_in2:
                    picked_status = st.selectbox("Attendance Status", config.ATTENDANCE_STATUSES, index=0)
                    picked_remarks = st.text_input("Remarks", value="Individual manual verification")
                    is_face_ver = st.checkbox("Visual / Face Verified", value=False)

                if st.form_submit_button("Record Student Attendance", use_container_width=True):
                    success, msg = database.mark_attendance_batch(picked_session_id, [{
                        "student_id": picked_student_id,
                        "status": picked_status,
                        "face_verified": 1 if is_face_ver else 0,
                        "remarks": picked_remarks
                    }])
                    if success:
                        st.success(f"Recorded: {picked_student_str} marked as {picked_status}.")
                    else:
                        st.error(f"Failed: {msg}")

        # TAB 3: REAL COMPUTER VISION VERIFICATION
        with tab_vision:
            st.subheader("📷 Visual Presence & Face Detection Verification")
            st.markdown(
                "> **Honest Implementation:** Uses real **OpenCV Haar Cascade Face Detection** "
                "(`haarcascade_frontalface_default.xml`) to verify physical presence in front of the lens. "
                "Draws bounding boxes, verifies human face presence, and calculates visual centeredness metrics."
            )

            v_col1, v_col2 = st.columns([1, 1])
            with v_col1:
                st.markdown("##### 1. Capture or Upload Image")
                input_source = st.radio("Choose Input Mode", ["Camera Snapshot", "File Upload"], horizontal=True)
                
                image_data = None
                if input_source == "Camera Snapshot":
                    image_data = st.camera_input("Take Live Verification Snapshot")
                else:
                    image_data = st.file_uploader("Upload Classroom/Student Photo", type=["jpg", "jpeg", "png"])

                selected_target_student = st.selectbox(
                    "Assign Detection to Student", 
                    list(student_choices.keys()) if 'student_choices' in locals() else []
                )

            with v_col2:
                st.markdown("##### 2. Real-time Detection Analysis")
                if image_data is not None:
                    with st.spinner("Processing image through Haar Cascade classifier..."):
                        detection_result = detector.process_image(image_data)
                    
                    if detection_result["annotated_image"] is not None:
                        st.image(detection_result["annotated_image"], caption="Annotated Computer Vision Output", use_container_width=True)
                    
                    if detection_result["face_detected"]:
                        st.success(f"✅ **{detection_result['details']}**")
                        st.metric("Estimated Visual Attention Score", f"{detection_result['estimated_visual_attention']}/100")
                        
                        if st.button("Confirm Attendance via Visual Presence", type="primary"):
                            target_id = student_choices[selected_target_student]
                            curr_sess_id = chosen_session_id if 'chosen_session_id' in locals() else 1
                            database.mark_attendance_batch(curr_sess_id, [{
                                "student_id": target_id,
                                "status": "Present",
                                "face_verified": 1,
                                "remarks": f"Haar Cascade Verified ({detection_result['face_count']} face(s) detected)"
                            }])
                            st.success(f"Attendance verified and recorded for {selected_target_student}!")
                    else:
                        st.warning("⚠️ No face detected in frame. Please adjust lighting, face camera directly, and recapture.")
                else:
                    st.info("Awaiting camera snapshot or uploaded photo to run detector.")

        # TAB 4: COMPLETE LOG & AUDIT
        with tab_history:
            st.subheader("📜 Historical Master Attendance Register")
            full_log_df = database.get_complete_attendance_log()
            
            if full_log_df.empty:
                st.info("No attendance records logged yet.")
            else:
                # Filter controls
                f1, f2, f3 = st.columns(3)
                with f1:
                    filter_status = st.multiselect("Filter by Status", config.ATTENDANCE_STATUSES, default=config.ATTENDANCE_STATUSES)
                with f2:
                    courses_in_log = full_log_df["course"].unique().tolist()
                    filter_course = st.multiselect("Filter by Course", courses_in_log, default=courses_in_log)
                with f3:
                    search_query = st.text_input("Search Student Name or Roll Number", "")

                filtered_log = full_log_df[
                    (full_log_df["status"].isin(filter_status)) &
                    (full_log_df["course"].isin(filter_course))
                ]
                if search_query:
                    filtered_log = filtered_log[
                        filtered_log["student_name"].str.contains(search_query, case=False) |
                        filtered_log["roll_number"].str.contains(search_query, case=False)
                    ]

                st.dataframe(
                    filtered_log[[
                        "session_date", "course", "roll_number", "student_name", 
                        "department", "status", "face_verified", "remarks"
                    ]],
                    use_container_width=True
                )
                st.caption(f"Showing {len(filtered_log)} of {len(full_log_df)} total records.")

# -------------------------------------------------------------
# PAGE 3: MULTIMODAL ENGAGEMENT AGENT
# -------------------------------------------------------------
elif selected_page == "🧠 Multimodal Engagement Agent":
    st.title("🧠 Multimodal Engagement Agent & Scoring Engine")
    st.markdown("Multi-factor observation scoring, composite Multimodal Engagement Index (MEI), and algorithmic pedagogical diagnostics.")

    if not has_data:
        st.warning("⚠️ Please load demo data or register students to access engagement analytics.")
    else:
        sessions_df = database.get_sessions_df()
        
        tab_eval, tab_agent, tab_decomp = st.tabs([
            "📝 Score Session Engagement",
            "🤖 Agent Diagnostics & Prescriptions",
            "📊 Multimodal Component Decomposition"
        ])

        with tab_eval:
            st.subheader("Evaluate Session Engagement Scores")
            st.markdown("Grade visual focus, auditory participation, and behavioral interaction for students in a selected session.")

            session_map = {f"#{r['id']} | {r['session_date']} | {r['course']}": r['id'] for _, r in sessions_df.iterrows()}
            selected_sess_label = st.selectbox("Select Session to Grade", list(session_map.keys()))
            eval_session_id = session_map[selected_sess_label]

            # Get students for this session
            att_records = database.get_session_attendance(eval_session_id)
            eng_records = database.get_session_engagement(eval_session_id)

            # Interactive Single Student Scorer
            st.markdown("##### Quick Multimodal Grading Form")
            with st.form("score_eval_form"):
                col_st1, col_st2 = st.columns([1, 1])
                with col_st1:
                    eval_stud_choice = st.selectbox(
                        "Student to Grade", 
                        [f"{r['roll_number']} - {r['name']}" for _, r in att_records.iterrows()]
                    )
                    eval_stud_roll = eval_stud_choice.split(" - ")[0]
                    eval_stud_id = att_records[att_records["roll_number"] == eval_stud_roll]["student_id"].values[0]
                    eval_stud_status = att_records[att_records["roll_number"] == eval_stud_roll]["status"].values[0]
                    st.caption(f"Current Session Attendance Status: **{eval_stud_status}**")

                with col_st2:
                    eval_notes = st.text_input("Qualitative Observations", value="Active participation during case study discussion")

                st.markdown("---")
                st.markdown("###### Multimodal Dimension Sliders (0 - 100)")
                s_col1, s_col2, s_col3 = st.columns(3)
                with s_col1:
                    v_score = st.slider("👁️ Visual Attention (Gaze, screen focus)", 0.0, 100.0, 80.0, 5.0)
                with s_col2:
                    a_score = st.slider("🎙️ Auditory (Spoken queries, debates)", 0.0, 100.0, 70.0, 5.0)
                with s_col3:
                    b_score = st.slider("📝 Behavioral (Quiz response, note-taking)", 0.0, 100.0, 85.0, 5.0)

                # Real-time MEI computation preview
                mei_calc = agent.calculate_mei(v_score, a_score, b_score, status=eval_stud_status)
                st.info(f"Calculated Composite MEI: **{mei_calc['composite_mei']}/100** | Tier: **{mei_calc['badge']}**")

                if st.form_submit_button("Save Multimodal Assessment", type="primary", use_container_width=True):
                    success, msg = database.record_engagement_batch(eval_session_id, [{
                        "student_id": int(eval_stud_id),
                        "visual_score": v_score,
                        "auditory_score": a_score,
                        "behavioral_score": b_score,
                        "composite_mei": mei_calc["composite_mei"],
                        "engagement_tier": mei_calc["tier"],
                        "notes": eval_notes
                    }])
                    if success:
                        st.success(f"Saved engagement score for {eval_stud_choice}!")
                        st.rerun()

            # Display Session Engagement Table
            st.markdown("##### Existing Session Multimodal Evaluations")
            if eng_records.empty:
                st.info("No engagement scores logged for this session yet.")
            else:
                st.dataframe(
                    eng_records[[
                        "roll_number", "name", "visual_score", "auditory_score", 
                        "behavioral_score", "composite_mei", "engagement_tier", "notes"
                    ]],
                    use_container_width=True
                )

        with tab_agent:
            st.subheader("🤖 Multimodal Agent Pedagogical Diagnostic Engine")
            st.markdown("Automated diagnostic rule-engine that synthesizes behavioral archetypes and generates targeted academic actions.")

            summary_df = database.get_student_analytics_summary()
            
            # Select student to analyze
            st_pick_label = st.selectbox(
                "Select Student for Diagnostic Inspection",
                [f"{r['roll_number']} - {r['name']} ({r['department']})" for _, r in summary_df.iterrows()]
            )
            st_pick_roll = st_pick_label.split(" - ")[0]
            student_stat = summary_df[summary_df["roll_number"] == st_pick_roll].iloc[0].to_dict()

            diagnosis = agent.diagnose_student(student_stat)

            # Display diagnostic card
            d_col1, d_col2 = st.columns([1, 2])
            with d_col1:
                st.markdown(f"### Archetype: **{diagnosis['profile']}**")
                st.markdown(f"**Risk Severity:** <span style='color:{diagnosis['risk_color']}; font-weight:bold;'>{diagnosis['risk_level']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Attendance Rate:** `{student_stat['attendance_percentage']:.1f}%`")
                st.markdown(f"**Average MEI:** `{student_stat['avg_mei']:.1f}/100`")
                st.markdown(f"**Summary:** *{diagnosis['summary']}*")

            with d_col2:
                st.markdown("##### 🔍 Algorithmic Behavioral Insights")
                for ins in diagnosis["insights"]:
                    st.markdown(f"- {ins}")
                
                st.markdown("##### 📋 Recommended Interventions for Academic Advisor")
                for rec in diagnosis["recommendations"]:
                    st.markdown(f"- {rec}")

        with tab_decomp:
            st.subheader("📊 Multimodal Component Decomposition")
            st.caption("Investigate how Visual, Auditory, and Behavioral modalities correlate across the class.")

            summary_df = database.get_student_analytics_summary()
            
            fig_hist = px.histogram(
                summary_df, 
                x=["avg_visual", "avg_auditory", "avg_behavioral"],
                barmode="overlay",
                nbins=20,
                opacity=0.7,
                labels={"value": "Score (0-100)", "variable": "Modality Component"},
                title="Distribution of Learning Modalities Across Student Cohort"
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380)
            st.plotly_chart(fig_hist, use_container_width=True)

# -------------------------------------------------------------
# PAGE 4: STUDENT DOSSIER & INDIVIDUAL ANALYTICS
# -------------------------------------------------------------
elif selected_page == "👤 Student Dossier & Analytics":
    st.title("👤 Student Dossier & Analytics")
    st.markdown("In-depth student-by-student academic performance, attendance percentage gauge, and longitudinal engagement trends.")

    if not has_data:
        st.warning("⚠️ Please load demo data or register students to access student profiles.")
    else:
        students_list = database.get_all_students()
        student_picker_dict = {f"{s['roll_number']} - {s['name']}": s['id'] for s in students_list}

        chosen_stud_label = st.selectbox("Search & Select Student Dossier", list(student_picker_dict.keys()))
        selected_student_id = student_picker_dict[chosen_stud_label]

        dossier = database.get_student_dossier(selected_student_id)
        s_info = dossier["student"]
        h_df = dossier["history_df"]

        # Student Profile Header
        st.markdown(f"### {s_info['name']} (`{s_info['roll_number']}`)")
        st.caption(f"{s_info['department']} | {s_info['semester']} | {s_info['section']} | {s_info['email']}")

        # Top Metric Cards
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
            st.metric("Total Lectures", f"{dossier['total_sessions']}")
        with col_m2:
            st.metric("Present Count", f"{dossier['present_count']}")
        with col_m3:
            st.metric("Late Count", f"{dossier['late_count']}")
        with col_m4:
            st.metric("Absent Count", f"{dossier['absent_count']}")
        with col_m5:
            st.metric("Average MEI", f"{dossier['avg_mei']}/100")

        st.markdown("---")

        c_g_left, c_g_right = st.columns([1, 2])

        with c_g_left:
            st.subheader("Attendance Percentage")
            att_val = dossier["attendance_percentage"]
            
            # Gauge Chart with University Thresholds
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=att_val,
                title={'text': "Cumulative Attendance %", 'font': {'size': 16}},
                number={'suffix': "%", 'font': {'size': 26}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "#1E293B"},
                    'steps': [
                        {'range': [0, 75], 'color': "#FEE2E2"},     # Red Danger (<75%)
                        {'range': [75, 85], 'color': "#FEF3C7"},    # Yellow Caution (75-85%)
                        {'range': [85, 100], 'color': "#DCFCE7"}    # Green Safe (85-100%)
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75.0
                    }
                }
            ))
            fig_gauge.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=260)
            st.plotly_chart(fig_gauge, use_container_width=True)

            if dossier["is_at_risk"]:
                st.error("🚨 **Detention Risk Active**: Attendance is below the mandatory 75% limit.")
            else:
                st.success("✅ **Good Standing**: Attendance satisfies regulatory criteria.")

        with c_g_right:
            st.subheader("Longitudinal Engagement Progression")
            if not h_df.empty and "composite_mei" in h_df.columns:
                valid_plot_df = h_df.dropna(subset=["composite_mei"])
                if not valid_plot_df.empty:
                    fig_trend = px.line(
                        valid_plot_df,
                        x="session_date",
                        y="composite_mei",
                        markers=True,
                        title="Session-by-Session Multimodal Engagement Index",
                        labels={"session_date": "Lecture Date", "composite_mei": "MEI Score"}
                    )
                    fig_trend.add_hline(y=65, line_dash="dash", line_color="orange", annotation_text="Baseline (65)")
                    fig_trend.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=260)
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("No engagement scores evaluated for this student yet.")
            else:
                st.info("No session records found.")

        # Session Attendance History Table
        st.subheader("Classroom Attendance & Engagement Log")
        if not h_df.empty:
            st.dataframe(
                h_df[[
                    "session_date", "course", "status", "face_verified", 
                    "visual_score", "auditory_score", "behavioral_score", "composite_mei", "engagement_tier"
                ]],
                use_container_width=True
            )

# -------------------------------------------------------------
# PAGE 5: REPORTS & DOWNLOADS
# -------------------------------------------------------------
elif selected_page == "📑 Reports & Downloads":
    st.title("📑 Academic Reports & Exports")
    st.markdown("Download official PDF academic performance audits and CSV data registers.")

    if not has_data:
        st.warning("⚠️ No records to export. Please load demo data or add student records.")
    else:
        summary_df = database.get_student_analytics_summary()
        kpis = database.get_overall_kpis()
        full_att_df = database.get_complete_attendance_log()

        r_col1, r_col2 = st.columns([1, 1])

        # PDF REPORT GENERATOR
        with r_col1:
            st.markdown("### 📄 Institutional PDF Academic Audit")
            st.markdown(
                "Generates a formal, printable academic audit report featuring executive KPI summaries, "
                "attendance statistics, multimodal engagement scores, early warning flags, and official signature blocks."
            )
            
            course_filter = st.selectbox("Select Course Scope for Report", ["All Courses"] + config.COURSES)
            term_str = st.text_input("Academic Term Label", f"Academic Year {config.ACADEMIC_YEAR} - Spring")

            with st.spinner("Compiling publication-grade PDF report..."):
                pdf_bytes = reports.generate_pdf_report(
                    summary_df=summary_df,
                    kpis=kpis,
                    course_name=course_filter,
                    academic_term=term_str
                )

            st.download_button(
                label="📥 Download Official PDF Report",
                data=pdf_bytes,
                file_name=f"Multimodal_Attendance_Audit_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.success("PDF ready for instant download.")

        # CSV EXPORTS
        with r_col2:
            st.markdown("### 📊 Tabular CSV Data Exports")
            st.markdown("Export structured datasets for spreadsheet analysis, institutional archiving, or external LMS ingestion.")

            # CSV 1: Student Summary
            csv_summary_bytes = reports.generate_csv_bytes(summary_df)
            st.download_button(
                label="📥 Download Student Performance Summary (CSV)",
                data=csv_summary_bytes,
                file_name=f"Student_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            # CSV 2: Full Attendance Register
            csv_att_bytes = reports.generate_csv_bytes(full_att_df)
            st.download_button(
                label="📥 Download Complete Attendance Register (CSV)",
                data=csv_att_bytes,
                file_name=f"Full_Attendance_Register_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            # CSV 3: At-Risk Students Filtered
            at_risk_df = summary_df[summary_df["is_at_risk"] == 1]
            if not at_risk_df.empty:
                csv_risk_bytes = reports.generate_csv_bytes(at_risk_df)
                st.download_button(
                    label=f"⚠️ Download At-Risk Students Roster ({len(at_risk_df)} Students) (CSV)",
                    data=csv_risk_bytes,
                    file_name=f"Detention_Risk_Students_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.markdown("---")
        st.subheader("Data Preview: Summary Roster")
        st.dataframe(
            summary_df[[
                "roll_number", "name", "department", "total_sessions", 
                "present_count", "absent_count", "attendance_percentage", "avg_mei", "is_at_risk"
            ]],
            use_container_width=True
        )

# -------------------------------------------------------------
# PAGE 6: STUDENT & SESSION DIRECTORY
# -------------------------------------------------------------
elif selected_page == "👥 Student & Session Directory":
    st.title("👥 Student & Classroom Directory")
    st.markdown("Manage student enrollments, course lecture sessions, and class rosters.")

    dir_tab1, dir_tab2 = st.tabs(["🎓 Manage Students", "📅 Manage Lecture Sessions"])

    with dir_tab1:
        st.subheader("Student Registry")
        
        # Add new student form
        with st.expander("➕ Enroll New Student", expanded=False):
            with st.form("add_student_form"):
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    new_roll = st.text_input("Roll Number *", placeholder="e.g. 2024-CS-150").strip()
                    new_name = st.text_input("Full Name *", placeholder="e.g. Priyanshu Saxena").strip()
                    new_email = st.text_input("Institutional Email", placeholder="e.g. p.saxena@college.edu").strip()
                with col_a2:
                    new_dept = st.selectbox("Department", config.DEPARTMENTS)
                    new_sem = st.selectbox("Semester", config.SEMESTERS, index=5)
                    new_sec = st.selectbox("Section", config.SECTIONS)

                if st.form_submit_button("Enroll Student", type="primary"):
                    if not new_roll or not new_name:
                        st.error("Roll Number and Name are mandatory fields.")
                    else:
                        success, msg = database.add_student(new_roll, new_name, new_email, new_dept, new_sem, new_sec)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        # Display and edit students
        students_df = database.get_students_df()
        if students_df.empty:
            st.info("No students enrolled yet.")
        else:
            st.dataframe(students_df[["roll_number", "name", "email", "department", "semester", "section", "created_at"]], use_container_width=True)

            # Delete student utility
            with st.expander("🗑️ Delete Student Record"):
                del_stud_choice = st.selectbox("Select Student to Remove", [f"{s['roll_number']} - {s['name']}" for _, s in students_df.iterrows()])
                del_roll = del_stud_choice.split(" - ")[0]
                del_id = students_df[students_df["roll_number"] == del_roll]["id"].values[0]
                
                if st.button("Permanently Delete Student & History", type="secondary"):
                    s_del, m_del = database.delete_student(int(del_id))
                    if s_del:
                        st.success(m_del)
                        st.rerun()
                    else:
                        st.error(m_del)

    with dir_tab2:
        st.subheader("Lecture Sessions Registry")
        with st.expander("➕ Schedule New Lecture Session", expanded=False):
            with st.form("new_session_form"):
                ns_course = st.selectbox("Course Title", config.COURSES)
                ns_date = st.date_input("Date", value=date.today())
                ns_time = st.selectbox("Slot", ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:15 AM - 12:15 PM", "02:00 PM - 03:00 PM"])
                ns_teacher = st.text_input("Lead Instructor", "Prof. Dr. R. Sharma")
                ns_notes = st.text_area("Session Agenda / Topics", "Unit 4: Advanced Architectural Concepts")

                if st.form_submit_button("Create Session", type="primary"):
                    sess_id = database.create_session(ns_course, str(ns_date), ns_time, ns_teacher, ns_notes)
                    st.success(f"Session #{sess_id} successfully scheduled!")
                    st.rerun()

        sessions_df = database.get_sessions_df()
        if sessions_df.empty:
            st.info("No classroom sessions recorded yet.")
        else:
            st.dataframe(sessions_df, use_container_width=True)

# -------------------------------------------------------------
# PAGE 7: SETTINGS & PROJECT OVERVIEW
# -------------------------------------------------------------
elif selected_page == "⚙️ Settings & Project Overview":
    st.title("⚙️ System Configuration & College Project Overview")
    st.markdown("Fine-tune Multimodal Engagement Index weights, regulatory thresholds, and inspect technical specifications.")

    t_cfg1, t_cfg2, t_cfg3 = st.tabs([
        "⚖️ Agent Scoring Weights", 
        "📘 Project Synopsis & Architecture",
        "🛠️ Technical Specifications"
    ])

    with t_cfg1:
        st.subheader("Multimodal Engagement Index (MEI) Weight Configuration")
        st.markdown(
            "The Multimodal Engagement Index fuses heterogeneous learning signals into a single standardized 0-100 metric:  \n"
            r"$$\text{MEI} = w_v \cdot S_{\text{visual}} + w_a \cdot S_{\text{auditory}} + w_b \cdot S_{\text{behavioral}} + w_t \cdot S_{\text{temporal}}$$"
        )

        with st.form("weights_form"):
            w_vis = st.slider("Visual Focus Weight ($w_v$)", 0.0, 1.0, st.session_state.agent_weights["visual"], 0.05)
            w_aud = st.slider("Auditory Participation Weight ($w_a$)", 0.0, 1.0, st.session_state.agent_weights["auditory"], 0.05)
            w_beh = st.slider("Behavioral Tasks Weight ($w_b$)", 0.0, 1.0, st.session_state.agent_weights["behavioral"], 0.05)
            w_tem = st.slider("Punctuality / Temporal Weight ($w_t$)", 0.0, 1.0, st.session_state.agent_weights["temporal"], 0.05)

            total_w = w_vis + w_aud + w_beh + w_tem
            st.write(f"Current Normalized Sum: **{total_w:.2f}**")

            if st.form_submit_button("Update Agent Weights", type="primary"):
                st.session_state.agent_weights = {
                    "visual": w_vis / total_w,
                    "auditory": w_aud / total_w,
                    "behavioral": w_beh / total_w,
                    "temporal": w_tem / total_w
                }
                st.success("Agent weights updated and normalized!")
                st.rerun()

    with t_cfg2:
        st.subheader("Academic Project Synopsis")
        st.markdown("""
        ### Project Title
        **Multimodal Attendance & Engagement Agent: An AI-Driven Academic Monitoring and Early Intervention System**

        ### Abstract
        Traditional classroom attendance monitoring captures binary presence (Present/Absent) but fails to detect 
        cognitive presence or classroom disengagement. The **Multimodal Attendance & Engagement Agent** overcomes this 
        limitation by integrating four distinct learning modalities:
        1. **Visual Attention**: Assessed via real OpenCV Haar Cascade face detection verifying physical presence and centeredness.
        2. **Auditory / Verbal Interaction**: Capturing dialogue, query frequency, and debate contributions.
        3. **Behavioral Interaction**: In-class quick quiz completion, note-taking, and task punctuality.
        4. **Temporal Consistency**: Punctuality patterns and cumulative attendance tracking against university 75% regulations.

        The system provides early warning alerts, longitudinal learning curves, automated PDF report generation, 
        and actionable pedagogical prescriptions for college educators.
        """)

    with t_cfg3:
        st.subheader("Technical Stack & Architecture")
        st.markdown("""
        | Layer | Technology | Purpose |
        | :--- | :--- | :--- |
        | **Frontend UI** | Streamlit | Responsive dashboard, widgets, interactive session state |
        | **Visualization** | Plotly | Dynamic scatter plots, gauges, radars, and bar charts |
        | **Data Store** | SQLite 3 | Relational database with foreign key constraints and indexes |
        | **Computer Vision** | OpenCV (`cv2`) | Haar Cascade human face detection for physical presence verification |
        | **Reporting** | ReportLab | Publication-grade academic audit PDF generation |
        | **Analytics** | Pandas & NumPy | Vectorized statistics, rolling averages, and aggregations |
        """)
