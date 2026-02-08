import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import uuid
import shutil
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from planner.utils.logger import setup_logger

logger = setup_logger(__name__)

from planner.ingestion.ocr import OCREngine
from planner.ingestion.cleaner import SyllabusCleaner
from planner.ai.extractor import Syllabusextractor
from planner.ai.validator import SyllabusValidator
from planner.agent.dialogue import DialogueAgent
from main import load_subjects_from_dict, get_next_version_dir, Subject, PlannerEngine, ExcelWriter

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (simple for local use)
sessions: Dict[str, Any] = {}

class ClarificationResponse(BaseModel):
    session_id: str
    answers: Dict[str, str]

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Semester Planner API is active"}

@app.post("/upload")
async def upload_syllabus(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")
    session_id = str(uuid.uuid4())
    temp_dir = f"temp/{session_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 1. Ingestion
    try:
        ocr = OCREngine()
        cleaner = SyllabusCleaner()
        extractor = Syllabusextractor()
        
        raw_text = ocr.extract_text(file_path)
        clean_text = cleaner.clean(raw_text)
        syllabus_data = extractor.extract(clean_text)
        
        # 2. Validation
        validator = SyllabusValidator()
        clarifications = validator.validate(syllabus_data)
        
        sessions[session_id] = {
            "syllabus_data": syllabus_data,
            "clarifications": clarifications,
            "file_path": file_path
        }
        
        return {
            "session_id": session_id,
            "clarifications": clarifications,
            "syllabus_data": syllabus_data
        }
    except Exception as e:
        logger.exception("Error during syllabus upload/processing")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine")
async def refine_plan(response: ClarificationResponse):
    session = sessions.get(response.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    syllabus_data = session["syllabus_data"]
    answers = response.answers
    
    # Apply answers (Simplified version of dialogue.py loop)
    for field, answer in answers.items():
        if field == "credits":
            syllabus_data["credits"] = int(answer)
        elif field == "exam_weightage":
            parts = "".join(c if c.isdigit() else " " for c in answer).split()
            if len(parts) >= 2:
                syllabus_data["exam_weightage"] = {"midterm": int(parts[0]), "final": int(parts[1])}
        elif "hours" in field:
            unit_no = int("".join(filter(str.isdigit, field)))
            for u in syllabus_data["units"]:
                if u["unit_no"] == unit_no:
                    u["minimum_hours"] = int(answer)
        elif "importance" in field:
            unit_no = int("".join(filter(str.isdigit, field)))
            for u in syllabus_data["units"]:
                if u["unit_no"] == unit_no:
                    u["importance"] = "IMP" if "high" in answer.lower() or "imp" in answer.lower() else "LESS_IMP"

    # Add general preferences if provided
    syllabus_data["difficulty_multiplier"] = 1.3 if answers.get("difficulty") == "yes" else 1.0
    syllabus_data["revision_weeks"] = 2 if answers.get("revision") == "yes" else 0

    # 3. Generate Plan
    subjects, semester_config = load_subjects_from_dict(syllabus_data)
    engine = PlannerEngine(subjects, semester_config)
    rows = engine.generate_plan_with_time()
    
    # 4. Save
    version_dir = get_next_version_dir()
    os.makedirs(version_dir, exist_ok=True)
    
    with open(os.path.join(version_dir, "syllabus_refined.json"), 'w') as f:
        json.dump(syllabus_data, f, indent=2)

    writer = ExcelWriter()
    for subject_name in set(r["subject"] for r in rows):
        writer.write_subject_sheet(
            subject_name,
            [r for r in rows if r["subject"] == subject_name]
        )

    out_file = os.path.join(version_dir, "semester_plan.xlsx")
    writer.save(out_file)
    
    return {
        "status": "success",
        "version": os.path.basename(version_dir),
        "excel_path": out_file
    }

from fastapi.responses import FileResponse

@app.get("/download/{version}")
async def download_plan(version: str):
    file_path = f"output/{version}/semester_plan.xlsx"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=f"semester_plan_{version}.xlsx")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
