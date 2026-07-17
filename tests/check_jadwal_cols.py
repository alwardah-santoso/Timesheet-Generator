from sheets_adapter import baca_data, TIMESHEET_SS_ID

data = baca_data(TIMESHEET_SS_ID, 'Jadwal Shifting')
print("Row 1 length:", len(data[0]))
print("Row 1 columns:", data[0])
