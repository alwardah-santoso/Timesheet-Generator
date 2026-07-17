from sheets_adapter import baca_data, TIMESHEET_SS_ID

for tab in ['Jadwal Shifting', 'Incident Open', 'Incident Closed']:
    data = baca_data(TIMESHEET_SS_ID, tab)
    print(f"=== Tab: {tab} ({len(data)} rows) ===")
    for row in data[:3]:
        print("  ", row[:10])
