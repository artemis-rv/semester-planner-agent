"""
Entry point of the application.

Responsibilities:
- Load structured syllabus data
- Load semester configuration
- Initialize PlannerEngine
- Trigger plan generation
- Pass output to ExcelWriter

This file orchestrates the flow.
No business logic should live here.
"""

import json
from planner.models.syllabus import Subject, Unit, Topic
from planner.engine.planner_engine import PlannerEngine
from planner.writers.excel_writer import ExcelWriter

def load_subjects(path: str):
    with open(path) as f:
        raw=json.load(f)

    semester_config=raw["semester"]
    subjects=[]

    for s in raw["subjects"]:
        units=[]
        for u in s["units"]:
            topics=[Topic(**t) for t in u["topics"]]
            units.append(Unit(
                unit_no=u["unit_no"],
                title=u["title"],
                importance=u["importance"],
                minimum_hours=u.get("minimum_hours"),
                topics=topics,
                self_study=u.get("self_study", [])
            ))

        subjects.append(Subject(
            code=s["code"],
            name=s["name"],
            credits=s["credits"],
            exam_weightage=s["exam_weightage"],
            units=units
        ))

        return subjects,semester_config
    

if __name__ == "__main__":
    subjects,semester_config = load_subjects("data/sample_syllabus.json")
    

    engine = PlannerEngine(subjects, semester_config)
    # rows = engine.generate_plan()
    rows = engine.generate_plan_with_time()
    print(rows)


    # writer = ExcelWriter()

    # for subject in set(r["subject"] for r in rows):
    #     writer.write_subject_sheet(
    #         subject,
    #         [r for r in rows if r["subject"] == subject]
    #     )

    # writer.save("output/semester_plan.xlsx")