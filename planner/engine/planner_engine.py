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


class PlannerEngine:
    """
    Converts syllabus data into a flat planning structure.
    
    """

    def __init__(self, subjects: list[Subject]):
        self.subjects = subjects

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
