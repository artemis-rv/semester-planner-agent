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

        # for row in rows:
        #     ws.append([
        #         row["unit"],
        #         row["importance"],
        #         row["unit_title"],
        #         row["topic"],
        #         row["subtopics"] if row["topic"]=="SELF STUDY" else "",
        #         row["minimum_hours"] or ""
        #     ])

        flag=0
        for row in rows:
            
            if row["topic"]=="SELF STUDY" and flag==0:
                ws.append(["","","",row["topic"],""])
                flag+=1
            
            if row["topic"]=="SELF STUDY":
                ws.append([
                    row["unit"],
                    row["importance"],
                    row["unit_title"],
                    # row["topic"],
                    row["subtopics"] if flag==1 else row["topic"],
                    row["minimum_hours"] or ""
                ])
            if row["topic"]!="SELF STUDY":
                ws.append([
                    row["unit"],
                    row["importance"],
                    row["unit_title"],
                    row["topic"],
                    # row["subtopics"] if row["topic"]=="SELF STUDY" else "",
                    row["minimum_hours"] or ""
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
        if "Sheet" in self.wb.sheetnames:
            del self.wb["Sheet"]
        self.wb.save(path)
