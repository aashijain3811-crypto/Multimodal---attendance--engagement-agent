"""
Multimodal Engagement Agent Module.
Implements the core analytical reasoning engine, Multimodal Engagement Index (MEI) 
fusion algorithm, anomaly detection heuristics, and personalized academic intervention generator.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from config import (
    DEFAULT_ENGAGEMENT_WEIGHTS, 
    ENGAGEMENT_TIERS, 
    ATTENDANCE_MANDATORY_THRESHOLD,
    ATTENDANCE_WARNING_THRESHOLD
)

class MultimodalEngagementAgent:
    """
    Intelligent Agent that synthesizes multiple observational modalities
    (Visual cues, Auditory/Verbal interaction, Behavioral response, and Temporal consistency)
    into a unified actionable engagement metric with academic diagnostics.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_ENGAGEMENT_WEIGHTS.copy()
        self._normalize_weights()

    def _normalize_weights(self):
        """Ensures weights sum to 1.0."""
        total = sum(self.weights.values())
        if total > 0:
            for k in self.weights:
                self.weights[k] = self.weights[k] / total

    def compute_temporal_score(self, status: str) -> float:
        """Translates attendance punctuality into a 0-100 temporal baseline."""
        status_map = {
            "Present": 100.0,
            "Late": 60.0,
            "Excused": 75.0,
            "Absent": 0.0
        }
        return status_map.get(status, 0.0)

    def calculate_mei(self, visual_score: float, auditory_score: float, 
                      behavioral_score: float, status: str = "Present") -> Dict[str, Any]:
        """
        Calculates the composite Multimodal Engagement Index (MEI).
        
        Formula:
            MEI = w_v * Visual + w_a * Auditory + w_b * Behavioral + w_t * Temporal
        """
        temporal_score = self.compute_temporal_score(status)
        
        # If student is absent, overall engagement for that session is 0
        if status == "Absent":
            composite = 0.0
            tier = "Critical"
        else:
            composite = (
                self.weights.get("visual", 0.30) * visual_score +
                self.weights.get("auditory", 0.25) * auditory_score +
                self.weights.get("behavioral", 0.30) * behavioral_score +
                self.weights.get("temporal", 0.15) * temporal_score
            )
            composite = max(0.0, min(100.0, round(composite, 2)))
            tier = self.classify_tier(composite)

        return {
            "visual_score": round(visual_score, 2),
            "auditory_score": round(auditory_score, 2),
            "behavioral_score": round(behavioral_score, 2),
            "temporal_score": temporal_score,
            "composite_mei": composite,
            "tier": tier,
            "badge": ENGAGEMENT_TIERS[tier]["badge"],
            "color": ENGAGEMENT_TIERS[tier]["color"]
        }

    def classify_tier(self, mei: float) -> str:
        """Categorizes composite MEI into one of 4 defined academic tiers."""
        for tier_name, bounds in ENGAGEMENT_TIERS.items():
            if bounds["min"] <= mei <= bounds["max"]:
                return tier_name
        return "Critical"

    def diagnose_student(self, student_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates individual student behavioral diagnostics and AI intervention plans.
        Uses rule-based heuristics on attendance percentage and multimodal components.
        """
        att_pct = student_stats.get("attendance_percentage", 0.0)
        avg_mei = student_stats.get("avg_mei", 0.0)
        avg_vis = student_stats.get("avg_visual", 0.0)
        avg_aud = student_stats.get("avg_auditory", 0.0)
        avg_beh = student_stats.get("avg_behavioral", 0.0)
        total_sessions = student_stats.get("total_sessions", 0)

        insights = []
        recommendations = []
        risk_level = "LOW"
        risk_color = "#10B981"
        action_required = False

        if total_sessions == 0:
            return {
                "profile": "New Student (No Records)",
                "risk_level": "NEUTRAL",
                "risk_color": "#6B7280",
                "summary": "No historical attendance or engagement records currently logged.",
                "insights": ["Awaiting initial session logging."],
                "recommendations": ["Log attendance in upcoming lecture session."],
                "action_required": False
            }

        # 1. Attendance Threshold Diagnostics
        if att_pct < ATTENDANCE_MANDATORY_THRESHOLD:
            risk_level = "CRITICAL"
            risk_color = "#EF4444"
            action_required = True
            insights.append(f"⚠️ Critical Detention Risk: Attendance is {att_pct:.1f}%, below university 75% requirement.")
            recommendations.append("Issue formal university attendance warning letter (Notice Form A).")
            recommendations.append("Schedule urgent counseling session with academic mentor.")
        elif att_pct < ATTENDANCE_WARNING_THRESHOLD:
            risk_level = "MEDIUM"
            risk_color = "#F59E0B"
            insights.append(f"⚡ Advisory Alert: Attendance is {att_pct:.1f}%, approaching danger boundary.")
            recommendations.append("Send gentle email alert reminding student of mandatory 75% rule.")

        # 2. Multimodal Behavioral Pattern Recognition
        if att_pct >= 80.0 and avg_aud < 45.0 and avg_vis >= 70.0:
            insights.append("👁️ 'Passive Observer' Pattern: High visual presence, but rarely speaks or asks verbal questions.")
            recommendations.append("Encourage participation via small peer-group discussions or digital polls before cold-calling.")

        if att_pct >= 80.0 and avg_vis < 50.0 and avg_beh < 50.0:
            insights.append("😴 'Distracted Presence' Pattern: Physical attendance is regular, but low visual focus and task completion.")
            recommendations.append("Seat in front row and incorporate frequent 2-minute quick-check interactive exercises.")

        if att_pct < 75.0 and avg_mei >= 75.0:
            insights.append("🌟 'Capable but Truant': High cognitive engagement and quiz scores when present, but skips lectures.")
            recommendations.append("Investigate timetable conflicts or commuting hurdles; emphasize collaborative in-class credit.")

        if att_pct >= 85.0 and avg_mei >= 80.0:
            insights.append("🏆 'Exemplary Scholar': Demonstrates consistent punctuality, active dialogue, and high visual focus.")
            recommendations.append("Consider nominating student for Peer Tutor / Undergraduate Teaching Assistant role.")

        if not insights:
            insights.append("⚖️ Balanced Profile: Attendance and multimodal participation are within normal collegiate bounds.")
            recommendations.append("Maintain continuous routine monitoring and reinforce consistent study habits.")

        # Overall summary statement
        if risk_level == "CRITICAL":
            summary = f"Requires immediate faculty intervention due to severe attendance deficit ({att_pct:.1f}%)."
        elif risk_level == "MEDIUM":
            summary = f"Student is at moderate risk. Attendance ({att_pct:.1f}%) requires proactive guidance."
        else:
            summary = f"Student is on track with satisfactory attendance ({att_pct:.1f}%) and engagement."

        return {
            "profile": self._generate_archetype_label(att_pct, avg_mei),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations,
            "action_required": action_required
        }

    def _generate_archetype_label(self, att_pct: float, avg_mei: float) -> str:
        """Produces a concise archetype tag for quick faculty scanning."""
        if att_pct >= 85.0 and avg_mei >= 80.0:
            return "Star Contributor"
        elif att_pct >= 75.0 and avg_mei >= 65.0:
            return "Steady Achiever"
        elif att_pct >= 75.0 and avg_mei < 65.0:
            return "Passive Participant"
        elif att_pct < 75.0 and avg_mei >= 65.0:
            return "Irregular but Capable"
        else:
            return "At-Risk / Disengaged"

    def generate_classroom_digest(self, summary_df: pd.DataFrame) -> Dict[str, Any]:
        """Synthesizes high-level actionable takeaways for the instructor."""
        if summary_df.empty:
            return {"alerts": ["No student data available."], "suggestions": []}

        alerts = []
        suggestions = []

        total_students = len(summary_df)
        at_risk = summary_df[summary_df["is_at_risk"] == 1]
        at_risk_count = len(at_risk)

        if at_risk_count > 0:
            pct_risk = (at_risk_count / total_students) * 100
            alerts.append(f"🚨 {at_risk_count} of {total_students} students ({pct_risk:.1f}%) are currently below the 75% attendance threshold.")
            suggestions.append("Export the At-Risk Student CSV roster and forward to Academic Affairs for formal warning notices.")

        avg_auditory_class = summary_df["avg_auditory"].mean()
        if avg_auditory_class < 55.0 and avg_auditory_class > 0:
            alerts.append(f"🎙️ Low Class-wide Verbal Interaction: Average verbal participation is {avg_auditory_class:.1f}/100.")
            suggestions.append("Introduce think-pair-share or designated student presentation segments to boost vocal interaction.")

        avg_vis_class = summary_df["avg_visual"].mean()
        if avg_vis_class < 60.0 and avg_vis_class > 0:
            alerts.append(f"👀 Gaze/Focus Slump: Visual attention averages {avg_vis_class:.1f}/100.")
            suggestions.append("Consider breaking 60-minute lectures into 20-minute conceptual blocks interspersed with interactive polls.")

        if not alerts:
            alerts.append("✅ Class attendance and multimodal engagement metrics are healthy.")
            suggestions.append("Continue current pedagogical methodology and reward top engaged students.")

        return {
            "alerts": alerts,
            "suggestions": suggestions
        }
