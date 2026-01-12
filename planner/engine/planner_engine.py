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

from planner.models.syllabus import Subject
from planner.utils.dates import generate_study_days,group_days_by_week
from datetime import datetime

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

        # Flatten all topics (excluding SELF STUDY headers)
        all_topics = []
        for subject in self.subjects:
            for unit in subject.units:
                for topic in unit.topics:
                    all_topics.append((subject, unit, topic))

        topics_per_week = max(1, len(all_topics) // total_weeks)

        plan_rows = []
        week_no = 1
        count = 0

        for subject, unit, topic in all_topics:
            if count >= topics_per_week:
                week_no += 1
                count = 0

            if week_no > total_weeks:
                week_no = total_weeks

            week_days = weeks[week_no]

            plan_rows.append({
                "subject": subject.name,
                "unit": unit.unit_no,
                "unit_title": unit.title,
                "importance": unit.importance,
                "topic": topic.topic,
                "week": week_no,
                "start_date": week_days[0],
                "end_date": week_days[-1],
                "estimated_hours": (
                    unit.minimum_hours // len(unit.topics)
                    if unit.minimum_hours
                    else None
                )
            })

            count += 1

        return plan_rows
