"""
Core planning logic.

Responsibilities:
- Convert syllabus data into planning rows
- Apply scheduling logic (weeks, dates)
- Estimate workload per topic
- Remain independent of Excel or UI

This is the brain of the planner.
If planning behavior is wrong, debug here first.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from planner.models.syllabus import Subject, Unit, Topic
from planner.utils.logger import setup_logger
from planner.utils.dates import generate_study_days,group_days_by_week

logger = setup_logger(__name__)

class PlannerEngine:
    """
    Converts syllabus data into a flat planning structure.
    
    """

    def __init__(self, subjects: list[Subject],semester_config):
        self.subjects = subjects
        self.semester_config = semester_config

    def generate_plan(self) -> list[dict]:
        plan_rows = []

        for subject in self.subjects:
            for unit in subject.units:
                for topic in unit.topics:
                    plan_rows.append({
                        "subject": subject.name,
                        "unit": unit.unit_no,
                        "unit_title": unit.title,
                        "importance": unit.importance,
                        "topic": topic.topic,
                        "subtopics": ", ".join(topic.subtopics),
                        "minimum_hours": unit.minimum_hours,
                        "self_study": False
                    })

                for ss in unit.self_study:
                    plan_rows.append({
                        "subject": subject.name,
                        "unit": unit.unit_no,
                        "unit_title": unit.title,
                        "importance": unit.importance,
                        "topic": "SELF STUDY",
                        "subtopics": ss,
                        "minimum_hours": None,
                        "self_study": True
                    })

        return plan_rows

    def generate_plan_with_time(self):
        start = datetime.strptime(
            self.semester_config["start_date"], "%Y-%m-%d"
        ).date()

        end = datetime.strptime(
            self.semester_config["end_date"], "%Y-%m-%d"
        ).date()

        rest_days = self.semester_config.get("rest_days", [])
        study_days = generate_study_days(start, end, rest_days)
        weeks = group_days_by_week(study_days)
        
        total_weeks = len(weeks)
        
        # 1. Handle Revision Weeks (Shrink the study period)
        # We'll set aside the last week(s) for revision
        revision_weeks_count = self.semester_config.get("revision_weeks", 0)
        study_weeks_limit = max(1, total_weeks - revision_weeks_count)
        
        # 2. Collect and Sort Topics
        all_topics = []
        for subject in self.subjects:
            # Get difficulty multiplier from subject or default
            diff_mult = getattr(subject, 'difficulty_multiplier', 1.0)
            
            # Simple heuristic: Units 1-3 are often midterm, 4-6 are final
            # In a better system, this would be explicitly in the JSON
            for unit in subject.units:
                for topic in unit.topics:
                    # Priority Score for sorting:
                    # Lower score = Earlier in schedule
                    priority_score = unit.unit_no
                    
                    all_topics.append({
                        "subject": subject,
                        "unit": unit,
                        "topic": topic,
                        "priority": priority_score,
                        "diff_mult": diff_mult
                    })

        # Sort by priority (Unit No) to ensure logical flow
        # This naturally "front-loads" lower unit numbers (Mid-exams)
        all_topics.sort(key=lambda x: x["priority"])

        # 3. Calculate Topics Per Week
        topics_per_week = max(1, len(all_topics) // study_weeks_limit)
        
        plan_rows = []
        current_week = 1
        count_in_week = 0

        for item in all_topics:
            subj = item["subject"]
            unit = item["unit"]
            topic = item["topic"]
            
            if count_in_week >= topics_per_week and current_week < study_weeks_limit:
                current_week += 1
                count_in_week = 0

            week_days = weeks[current_week]

            # 4. Weighted Hour Calculation
            base_hours = unit.minimum_hours or 10
            topic_count = len(unit.topics)
            hours_per_topic = (base_hours / topic_count) * item["diff_mult"]
            
            # Boost hours if unit is marked "IMP"
            if unit.importance == "IMP":
                hours_per_topic *= 1.2

            plan_rows.append({
                "subject": subj.name,
                "unit": unit.unit_no,
                "unit_title": unit.title,
                "importance": unit.importance,
                "topic": topic.topic,
                "subtopics": topic.subtopics,
                "self_study": False,
                "week": current_week,
                "start_date": week_days[0],
                "end_date": week_days[-1],
                "estimated_hours": round(hours_per_topic, 1)
            })

            count_in_week += 1

        # 5. Add Revision Rows for the final weeks
        if revision_weeks_count > 0:
            for rw in range(study_weeks_limit + 1, total_weeks + 1):
                week_days = weeks[rw]
                plan_rows.append({
                    "subject": "ALL SUBJECTS",
                    "unit": 0,
                    "unit_title": "REVISION CYCLE",
                    "importance": "IMP",
                    "topic": f"Final Revision Cycle - Week {rw}",
                    "subtopics": [],
                    "self_study": False,
                    "week": rw,
                    "start_date": week_days[0],
                    "end_date": week_days[-1],
                    "estimated_hours": self.semester_config.get("daily_hours", 3) * 5
                })

        return plan_rows
