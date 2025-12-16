from openpyxl import load_workbook

REQUIRED_COLS = ["TeamID", "Team Name", "GitHub Emails"]

def read_excel(path):
    wb = load_workbook(path)
    ws = wb.active

    headers = [c.value for c in ws[1]]
    for col in REQUIRED_COLS:
        if col not in headers:
            raise ValueError(f"Missing column: {col}")

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(headers, row)))

    return rows
