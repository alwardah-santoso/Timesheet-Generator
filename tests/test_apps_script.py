from sheets_adapter import kirim_perintah, TIMESHEET_SS_ID

res = kirim_perintah({
    'action': 'format',
    'id': TIMESHEET_SS_ID,
    'tab_name': 'Summary'
})
print("Format response:", res)
