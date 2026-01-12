"""
Excel output generation.

Responsibilities:
- Create workbooks and worksheets
- Apply formatting and styling
- Render planning rows into Excel layout
- Handle metadata and presentation details

No planning or date logic should live here.
If Excel looks wrong but logic is right, debug here.
"""


from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side

import socket

class ExcelWriter:

    def __init__(self):
        self.wb=Workbook()


    def write_subject_sheet(self, subject_name: str, rows: list[dict]):
        ws = self.wb.create_sheet(title=subject_name[:31])

        headers = ["Unit", "Importance", "Chapters", "Topics", "Min Hours"]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        # for row in rows:
        #     ws.append([
        #         row["unit"],
        #         row["importance"],
        #         row["unit_title"],
        #         row["topic"],
        #         row["subtopics"] if row["topic"]=="SELF STUDY" else "",
        #         row["minimum_hours"] or ""
        #     ])

        self_study_written = set()

        for row in rows:
            unit = row["unit"]

            # NORMAL TOPICS
            if not row["self_study"]:
                ws.append([
                    row["unit"],
                    row["importance"],
                    row["unit_title"],
                    row["topic"],
                    row["minimum_hours"] or ""
                ])
                continue

            # SELF STUDY HEADER (once per unit)
            if row["topic"] == "SELF STUDY" and unit not in self_study_written:
                ws.append([
                    "", "", "",
                    "SELF STUDY",
                    ""
                ])
                self_study_written.add(unit)
                # continue

            # SELF STUDY ITEMS (below header, Topic column only)
            ws.append([
                "", "", "",
                row["subtopics"],
                ""
            ])


        self._apply_unit_separators(ws)

    def _apply_unit_separators(self, ws):
        thin = Side(style="thin")
        border = Border(top=thin, bottom=thin)

# ws is a worksheet
# iter_rows() returns rows as tuples of cells
# min_row=2 means: Skip row 1 (the header)

        for row in ws.iter_rows(min_row=2):
            if row[3].value == "SELF STUDY":
                row[3].font=Font(bold=True)
                row[3].border = border
                # for cell in row:

    def save(self, path: str):
        props = self.wb.properties
        props.creator = socket.gethostname()
        props.lastModifiedBy = socket.gethostname()
        props.title = "Semester Study Planner"
        props.description = "Auto-generated semester planner using Python"
        if "Sheet" in self.wb.sheetnames:
            del self.wb["Sheet"]
        self.wb.save(path)
