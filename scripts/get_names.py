from sheets_adapter import baca_data, TIMESHEET_SS_ID

data = baca_data(TIMESHEET_SS_ID, 'Jadwal Shifting')
names = []
for row in data[2:]:
    if row and str(row[0]).strip():
        names.append(str(row[0]).strip())
print("Consultant names:", names)
