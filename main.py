"""
Entry point of the application (Full Phase 2).

Responsibilities:
- Ingest syllabus files
- Validate data via AI/Schema
- Run Dialogue loop for missing info
- Generate plan with versioning
"""

import json
import os
import sys
from datetime import datetime
from planner.utils.logger import setup_logger
from dotenv import load_dotenv
from planner.models.syllabus import Subject, Unit, Topic
from planner.engine.planner_engine import PlannerEngine
from planner.writers.excel_writer import ExcelWriter
from planner.ingestion.ocr import OCREngine
from planner.ingestion.cleaner import SyllabusCleaner
from planner.ai.extractor import Syllabusextractor
from planner.ai.validator import SyllabusValidator
from planner.agent.dialogue import DialogueAgent

logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

def get_next_version_dir(base_dir="output"):
    """Returns the path for the next version directory, e.g., output/v1, output/v2."""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        return os.path.join(base_dir, "v1")
    
    versions = [d for d in os.listdir(base_dir) if d.startswith('v') and d[1:].isdigit()]
    if not versions:
        return os.path.join(base_dir, "v1")
    
    next_ver = max([int(v[1:]) for v in versions]) + 1
    return os.path.join(base_dir, f"v{next_ver}")

def ingest_syllabus(file_path: str):
    """
    Ingests a syllabus file (PDF/DOCX/Image), cleans it, and extracts structured data.
    """
    ocr = OCREngine()
    cleaner = SyllabusCleaner()
    extractor = Syllabusextractor()

    logger.info(f"--- Processing: {file_path} ---")
    raw_text = ocr.extract_text(file_path)
    clean_text = cleaner.clean(raw_text)
    
    logger.info("--- Extracting structured data via AI ---")
    syllabus_data = extractor.extract(clean_text)
    
    return syllabus_data

def refine_syllabus_data(syllabus_data: dict):
    """Runs validation and dialogue loop to polish the data."""
    validator = SyllabusValidator()
    agent = DialogueAgent()
    
    clarifications = validator.validate(syllabus_data)
    
    if clarifications:
        logger.info(f"\n[!] Detected {len(clarifications)} items that need clarification.")
        syllabus_data = agent.run_clarification_loop(syllabus_data, clarifications)
    else:
        # Ask preference questions even if data is valid
        syllabus_data = agent.run_clarification_loop(syllabus_data, [])
        
    return syllabus_data

def load_subjects_from_dict(raw: dict):
    """Converts raw dict (from JSON or AI) into Subject objects."""
    # Use defaults if semester config is missing
    semester_config = raw.get("semester", {
        "available_weeks": 15,
        "priority_focus": "IMP",
        "daily_hours": 3,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now().replace(month=datetime.now().month+4)).strftime("%Y-%m-%d")
    })
    
    # Merge preferences back into semester_config for the engine
    semester_config["difficulty_multiplier"] = raw.get("difficulty_multiplier", 1.0)
    semester_config["revision_weeks"] = raw.get("revision_weeks", 0)

    subjects = []
    # Handle single subject or list of subjects
    raw_subjects = raw["subjects"] if "subjects" in raw else ([raw] if "units" in raw else [])
    
    for s in raw_subjects:
        units = []
        for u in s["units"]:
            topics = [Topic(**t) for t in u["topics"]]
            units.append(Unit(
                unit_no=u["unit_no"],
                title=u["title"],
                importance=u["importance"],
                minimum_hours=u.get("minimum_hours"),
                topics=topics,
                self_study=u.get("self_study", [])
            ))

        subjects.append(Subject(
            code=s.get("code", "N/A"),
            name=s.get("name", "Unknown Subject"),
            credits=s.get("credits", 3),
            exam_weightage=s.get("exam_weightage", {"mid": 30, "end": 70}),
            units=units,
            difficulty_multiplier=raw.get("difficulty_multiplier", 1.0)
        ))

    return subjects, semester_config

def main():
    if len(sys.argv) < 2:
        logger.info("Usage: python main.py <syllabus_file_or_json>")
        sys.exit(1)

    path = sys.argv[1]
    
    if not os.path.exists(path):
        logger.error(f"Error: File not found at {path}")
        sys.exit(1)

    # 1. Ingestion
    if not path.lower().endswith('.json'):
        raw_data = ingest_syllabus(path)
    else:
        with open(path) as f:
            raw_data = json.load(f)

    # 2. Refinement (Validation + Dialogue)
    refined_data = refine_syllabus_data(raw_data)
    
    # 3. Model Loading
    subjects, semester_config = load_subjects_from_dict(refined_data)
    
    # 4. Plan Generation
    logger.info(f"--- Generating study plan for {len(subjects)} subjects ---")
    engine = PlannerEngine(subjects, semester_config)
    rows = engine.generate_plan_with_time()
    
    # 5. Output with Versioning
    version_dir = get_next_version_dir()
    os.makedirs(version_dir, exist_ok=True)
    
    # Save the polished JSON for audit
    with open(os.path.join(version_dir, "syllabus_refined.json"), 'w') as f:
        json.dump(refined_data, f, indent=2)

    writer = ExcelWriter()
    for subject_name in set(r["subject"] for r in rows):
        writer.write_subject_sheet(
            subject_name,
            [r for r in rows if r["subject"] == subject_name]
        )

    out_file = os.path.join(version_dir, "semester_plan.xlsx")
    writer.save(out_file)
    logger.info(f"\n[SUCCESS] Plan Version {os.path.basename(version_dir)} generated at: {out_file}")

if __name__ == "__main__":
    main()