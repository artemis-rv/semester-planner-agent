# key responsibilities:
# One master sheet
# One sheet per subject
# Merged cells for units

from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side

class ExcelWriter:

    def __init__(self):
        self.wb=Workbook()


    def write_subject_sheet(self, subject_name: str, rows: list[dict]):
        ws = self.wb.create_sheet(title=subject_name[:31])

        headers = ["Unit", "Importance", "Chapters", "Topics", "Min Hours"]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            ws.append([
                row["unit"],
                row["importance"],
                row["topic"],
                row["subtopics"],
                row["minimum_hours"] or ""
            ])

        self._apply_unit_separators(ws)

    def _apply_unit_separators(self, ws):
        thin = Side(style="thin")
        border = Border(bottom=thin)

# ws is a worksheet
# iter_rows() returns rows as tuples of cells
# min_row=2 means: Skip row 1 (the header)

        for row in ws.iter_rows(min_row=2):
            if row[2].value == "SELF STUDY":
                for cell in row:
                    cell.border = border

    def save(self, path: str):
        if "Sheet" in self.wb.sheetnames:
            del self.wb["Sheet"]
        self.wb.save(path)
