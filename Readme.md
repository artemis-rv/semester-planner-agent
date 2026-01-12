# Semester Planner Agent

## Overview

Semester Planner Agent is a local automation system that converts academic syllabi into structured, multi-sheet Excel planners.

The system is designed to handle real-world syllabus complexity, including:

* Units, topics, and sub-topics
* Importance levels (IMP / LESS_IMP)
* Self-study sections
* Minimum recommended hours
* Multiple subjects per semester
* Planner regeneration with versioning (later phases)

The project follows production-style software engineering practices and is built incrementally with clear separation of concerns.

---

## Project Goals

* Transform unstructured or semi-structured academic syllabi into usable study planners
* Support image-based and scanned documents (OCR in later phases)
* Generate clean, readable Excel planners with:

  * Multiple sheets per subject
  * A master overview sheet
  * Merged cells and visual separators
* Apply SOLID principles and maintainable architecture

---

## Completed Phases

### Phase 1 – Core Planner Engine
- Designed structured syllabus data models
- Implemented planner engine with clean separation of concerns
- Generated multi-sheet Excel planners
- Implemented self-study section rendering
- Followed SOLID principles in code organization

---

## Current Phase

**Phase 2A – Time-Aware Planning Logic (In Progress)**

Focus:
- Semester date handling
- Rest day exclusion
- Week-based topic allocation
- Soft workload estimation

---

## Repository Structure

```
semester-planner-agent/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   └── planner_config.yaml
│
├── data/
│   └── sample_syllabus.json
│
├── planner/
│   ├── models/
│   │   └── syllabus.py
│   │
│   ├── engine/
│   │   └── planner_engine.py
│   │
│   ├── writers/
│   │   └── excel_writer.py
│   │
│   └── utils/
│       └── dates.py
│
├── output/
│   └── semester_plan.xlsx
│
└── main.py
```

---

## How It Works (Current)

1. Academic syllabus data is provided in structured JSON format
2. Semester configuration (start date, end date, rest days) is loaded
3. The planner engine converts syllabus hierarchy into time-aware planning rows
4. Topics are distributed across semester weeks with soft hour estimation
5. The Excel writer generates formatted `.xlsx` files
6. Each subject is written to a separate sheet

---

## Requirements

* Python 3.10+
* openpyxl

Install dependencies:

```
pip install -r requirements.txt
```

---

## Running the Project

```
python main.py
```

Output:

* `output/semester_plan.xlsx`

---

## Design Principles

* Separation of concerns
* No business logic inside Excel writer
* Data models independent of file formats
* Extensible architecture for OCR and AI layers

---

## In Progress

- Date-based semester planning
- Rest day handling
- Weekly workload estimation

---

## Planned Features (Upcoming Phases)

* OCR support for images and scanned PDFs
* LLM-based structured syllabus extraction
* Interactive clarification questions
* Planner versioning and regeneration
* Local web-based UI

---

## License

This project is intended for personal and educational use.
