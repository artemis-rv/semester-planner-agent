"""
Data models for syllabus structure.

Defines:
- Subject
- Unit
- Topic

Responsibilities:
- Represent academic hierarchy
- Hold raw, structured data
- No logic, no computation, no formatting

If you need to change data shape, edit this file.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Topic:
    topic: str
    subtopics: List[str]


@dataclass
class Unit:
    unit_no: int
    title: str
    importance: str  # IMP / LESS_IMP
    minimum_hours: Optional[int]
    topics: List[Topic]
    self_study: List[str]


@dataclass
class Subject:
    code: str
    name: str
    credits: int
    exam_weightage: dict
    units: List[Unit]