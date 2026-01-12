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


def generate_study_days(start: date, end: date, rest_days: list[str]):
    rest_days=set(rest_days)                            #constant lookup time
    study_days=[]

    for d in daterange(start,end):
        if d.strftime("%A") not in rest_days:               #converts date into corresponding days
            study_days.append(d)

    return study_days


def group_days_by_week(study_days: list[date]):
    """
    Groups dates into week numbers starting from week 1.
    Week 1 = first study week of semester.
    """

    weeks=defaultdict(list)
    week_no=1

    for d in study_days:
        if weeks[week_no] and d.weekday() == 0:
            week_no += 1
        weeks[week_no].append(d)

    return dict(weeks)
