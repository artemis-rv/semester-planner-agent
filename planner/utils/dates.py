"""
Date and time utility functions.

Responsibilities:
- Generate date ranges
- Exclude rest days
- Group study days into relative semester weeks

This file defines what 'time' means in the planner.
No syllabus or Excel logic should appear here.
"""


from datetime import date, timedelta
from collections import defaultdict

#timedelta move forward 1 day at a time
#defaultdict: no constant key checks required


def daterange(start: date, end: date):
    current=start
    while current<=end:
        yield current                           #produces 1 value at a time
        current+=timedelta(days=1)              #increments 1 calender day


