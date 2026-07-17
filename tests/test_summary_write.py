from sheets_adapter import kirim_perintah, baca_data, TIMESHEET_SS_ID

res_clear = kirim_perintah({'action': 'clear', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary'})
print("Clear result:", res_clear)

res_append = kirim_perintah({'action': 'append', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary', 'row': ['A', 'B', 'C']})
print("Append result:", res_append)

data = baca_data(TIMESHEET_SS_ID, 'Summary')
print("Summary read after append:", data)
