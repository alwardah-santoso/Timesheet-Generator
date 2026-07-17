import sys
from sheets_adapter import baca_data, kirim_perintah, TIMESHEET_SS_ID

print("Reading Summary tab from Google Spreadsheet...")
data = baca_data(TIMESHEET_SS_ID, 'Summary')
print(f"Rows in Summary: {len(data)}")
for row in data[:10]:
    print(row)
