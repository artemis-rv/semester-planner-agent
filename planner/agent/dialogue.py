from planner.utils.logger import setup_logger

logger = setup_logger(__name__)

class DialogueAgent:
    """
    Handles interactive Q&A with the user to fill gaps in the syllabus.
    """

    def run_clarification_loop(self, syllabus_data: Dict[str, Any], clarifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Loops through clarifications and asks the user for input.
        Returns the updated syllabus_data.
        """
        logger.info("\n--- Agent Dialogue Loop ---")
        logger.info("I need a few more details to create a perfect plan.\n")

        for task in clarifications:
            context = f"[{task.get('context')}] " if task.get('context') else ""
            answer = input(f"{context}{task['question']}\n> ")
            
            # Update data based on field name
            field = task['field']
            if field == "credits":
                try:
                    syllabus_data["credits"] = int(answer)
                except ValueError:
                    syllabus_data["credits"] = 3 # Default
            elif field == "exam_weightage":
                # Simple parser for "30/70" or "30 70"
                parts = "".join(c if c.isdigit() else " " for c in answer).split()
                if len(parts) >= 2:
                    syllabus_data["exam_weightage"] = {
                        "midterm": int(parts[0]),
                        "final": int(parts[1])
                    }
                else:
                    syllabus_data["exam_weightage"] = {"midterm": 30, "final": 70}
            elif "hours" in field:
                # Find the unit in data
                unit_no = int("".join(filter(str.isdigit, field)))
                for u in syllabus_data["units"]:
                    if u["unit_no"] == unit_no:
                        try:
                            u["minimum_hours"] = int(answer)
                        except ValueError:
                            u["minimum_hours"] = 10
            elif "importance" in field:
                unit_no = int("".join(filter(str.isdigit, field)))
                for u in syllabus_data["units"]:
                    if u["unit_no"] == unit_no:
                        u["importance"] = "IMP" if "high" in answer.lower() or "imp" in answer.lower() else "LESS_IMP"

        # General Preference Questions
        print("\n--- Planning Preferences ---")
        diff = input("Is this subject difficult? (yes/no)\n> ")
        syllabus_data["difficulty_multiplier"] = 1.3 if diff.lower().startswith('y') else 1.0
        
        rev = input("Do you want dedicated revision weeks before exams? (yes/no)\n> ")
        syllabus_data["revision_weeks"] = 2 if rev.lower().startswith('y') else 0

        return syllabus_data

if __name__ == "__main__":
    # Test
    agent = DialogueAgent()
    data = {"name": "Test", "units": []}
    tasks = [{"field": "credits", "question": "Credits?"}]
    # Note: input() will block in a real terminal, here it's just for structure
    # Updated = agent.run_clarification_loop(data, tasks)
