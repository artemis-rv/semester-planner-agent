import json
from typing import Dict, Any, List
from planner.utils.logger import setup_logger

logger = setup_logger(__name__)

class SyllabusValidator:
    """
    Validates extracted syllabus JSON and identifies gaps or ambiguities.
    """

    def validate(self, syllabus_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns a list of clarifications needed.
        Each clarification is a dict with: 'field', 'context', 'question'.
        """
        clarifications = []

        # Check Subject level
        if not syllabus_data.get("credits"):
            clarifications.append({
                "type": "missing_info",
                "field": "credits",
                "question": f"How many credits is the course '{syllabus_data.get('name')}' worth?"
            })

        if not syllabus_data.get("exam_weightage"):
            clarifications.append({
                "type": "missing_info",
                "field": "exam_weightage",
                "question": "What is the exam weightage (Midterm vs Final %)? (e.g. 30/70)"
            })

        # Check Unit level
        for unit in syllabus_data.get("units", []):
            u_no = unit.get("unit_no")
            if not unit.get("minimum_hours"):
                clarifications.append({
                    "type": "missing_info",
                    "field": f"unit_{u_no}_hours",
                    "context": f"Unit {u_no}: {unit.get('title')}",
                    "question": f"How many hours should be allocated for Unit {u_no}?"
                })
            
            # Check for generic importance
            if unit.get("importance") not in ["IMP", "LESS_IMP"]:
                clarifications.append({
                    "type": "ambiguity",
                    "field": f"unit_{u_no}_importance",
                    "context": f"Unit {u_no}",
                    "question": f"Is Unit {u_no} high priority (IMP) or low priority (LESS_IMP)?"
                })

        return clarifications

    def is_consistent(self, syllabus_data: Dict[str, Any]) -> bool:
        """Returns True if no critical information is missing."""
        return len(self.validate(syllabus_data)) == 0

if __name__ == "__main__":
    # Test
    sample = {
        "name": "Test Course",
        "units": [{"unit_no": 1, "title": "Intro"}]
    }
    validator = SyllabusValidator()
    logger.info(json.dumps(validator.validate(sample), indent=2))
