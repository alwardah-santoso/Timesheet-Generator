from sheets_adapter import baca_data, TIMESHEET_SS_ID

for tab in ['Open Insiden', 'Closed Insiden', 'Backup']:
    data = baca_data(TIMESHEET_SS_ID, tab)
    print(f"=== Tab: {tab} ({len(data)} rows) ===")
    for row in data[:5]:
        print("  ", row)
