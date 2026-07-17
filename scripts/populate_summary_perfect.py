from datetime import datetime
from sheets_adapter import kirim_perintah, build_dataframes, get_shifts_for_name, baca_data, TIMESHEET_SS_ID
from core import process_from_sheets_data

print("1. Fetching data from Google Sheets...")
cache = build_dataframes(TIMESHEET_SS_ID)

consultant_name = "Ulil Amri"
shifts = get_shifts_for_name(cache, consultant_name)
names, result = process_from_sheets_data(shifts, consultant_name)

days = result['days']

work_days = len([d for d in days if d['type'] not in ('OFF', 'IS')])
off_days = len([d for d in days if d['type'] == 'OFF'])

total_open = 0
total_closed = 0
for d in days:
    if d['type'] == 'S12':
        total_open += sum(d.get('open_s1', {}).values()) + sum(d.get('open_s2', {}).values())
        total_closed += sum(d.get('closed_s1', {}).values()) + sum(d.get('closed_s2', {}).values())
    elif d['type'] == 'S23':
        total_open += sum(d.get('open_s2', {}).values()) + sum(d.get('open_s3', {}).values())
        total_closed += sum(d.get('closed_s2', {}).values()) + sum(d.get('closed_s3', {}).values())
    elif d['type'] not in ('OFF', 'IS'):
        total_open += sum(d.get('open', {}).values())
        total_closed += sum(d.get('closed', {}).values())

def fmt_date(d_val):
    s = str(d_val)
    if 'T' in s:
        s = s.split('T')[0]
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return s

print("2. Clearing Google Spreadsheet Summary tab...")
kirim_perintah({'action': 'clear', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary'})

rows = [
    ["TIMESHEET CLEANER — SUMMARY & DATA PREVIEW", "", "", "", "", ""],
    ["Pilih Nama Konsultan:", result['employee_name'], "Periode:", "Juni 2026", "", ""],
    ["STATISTIK BULANAN", "", "", "", "", ""],
    ["Hari Kerja", work_days, "Hari OFF", off_days, "Open Ticket", total_open],
    ["Closed Ticket", total_closed, "", "", "", ""],
    ["DATA PREVIEW HARIAN", "", "", "", "", ""],
    ["Tanggal", "Shift", "Jam Kerja", "Open Ticket", "Closed Ticket", "Remark"]
]

for d in days:
    shift_type = d['type']
    if shift_type in ('OFF', 'IS'):
        jam = "-"
    else:
        jam = f"{d.get('start', '-') } - {d.get('end', '-')}"
    
    op = 0
    cl = 0
    if shift_type == 'S12':
        op = sum(d.get('open_s1', {}).values()) + sum(d.get('open_s2', {}).values())
        cl = sum(d.get('closed_s1', {}).values()) + sum(d.get('closed_s2', {}).values())
    elif shift_type == 'S23':
        op = sum(d.get('open_s2', {}).values()) + sum(d.get('open_s3', {}).values())
        cl = sum(d.get('closed_s2', {}).values()) + sum(d.get('closed_s3', {}).values())
    elif shift_type not in ('OFF', 'IS'):
        op = sum(d.get('open', {}).values())
        cl = sum(d.get('closed', {}).values())
    
    rem = "OFF" if shift_type == 'OFF' else ("Izin Sakit" if shift_type == 'IS' else d.get('remark', shift_type))
    rows.append([fmt_date(d['date']), d['shift'], jam, op if op > 0 else 0, cl if cl > 0 else 0, rem])

print(f"3. Appending {len(rows)} clean rows to Summary...")
for idx, r in enumerate(rows):
    kirim_perintah({'action': 'append', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary', 'row': r})
    if idx % 10 == 0:
        print(f"  Row {idx+1}/{len(rows)}...")

print("Done! Verifying read...")
verif = baca_data(TIMESHEET_SS_ID, 'Summary')
print("Total rows:", len(verif))
for r in verif[:8]:
    print(" ", r)
