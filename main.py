import json
from planner.models.syllabus import Subject, Unit, Topic
from planner.engine.planner_engine import PlannerEngine
from planner.writers.excel_writer import ExcelWriter

def load_subjects(path: str):
    with open(path) as f:
        raw=json.load(f)

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

        return subjects
    

if __name__ == "__main__":
    subjects = load_subjects("data/sample_syllabus.json")

    engine = PlannerEngine(subjects)
    rows = engine.generate_plan()

    writer = ExcelWriter()

    for subject in set(r["subject"] for r in rows):
        writer.write_subject_sheet(
            subject,
            [r for r in rows if r["subject"] == subject]
        )

    writer.save("output/semester_plan.xlsx")