import time
from sheets_adapter import kirim_perintah, baca_data, TIMESHEET_SS_ID

def col_letter(n):
    # n=1 -> A, n=2 -> B, ..., n=30 -> AD, n=31 -> AE
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

print("1. Clearing Summary sheet in Google Spreadsheet...")
res = kirim_perintah({'action': 'clear', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary'})
print("Clear result:", res)

rows_to_append = [
    ["TIMESHEET CLEANER — SUMMARY & DATA PREVIEW", "", "", "", "", ""],
    ["", "", "", "", "", ""],
    ["Pilih Nama Konsultan:", "Ulil Amri", "", "Periode:", "Juni 2026", ""],
    ["", "", "", "", "", ""],
    ["STATISTIK BULANAN", "", "", "", "", ""],
    [
        "Hari Kerja", '=COUNTIF(B11:B40, "<>OFF")-COUNTIF(B11:B40, "IS")',
        "Hari OFF", '=COUNTIF(B11:B40, "OFF")',
        "Open Ticket", '=SUM(D11:D40)',
        "Closed Ticket", '=SUM(E11:E40)'
    ],
    ["", "", "", "", "", ""],
    ["DATA PREVIEW HARIAN", "", "", "", "", ""],
    ["Tanggal", "Shift", "Jam Kerja", "Open Ticket", "Closed Ticket", "Remark"]
]

# Build 30 daily rows
for day in range(1, 31):
    row_num = 10 + day
    c_letter = col_letter(day + 1) # day 1 is col B (2) in Jadwal Shifting
    date_str = f"{day:02d}/06/2026"
    shift_formula = f'=INDEX(\'Jadwal Shifting\'!{c_letter}$3:{c_letter}$17, MATCH($B$3, \'Jadwal Shifting\'!$A$3:$A$17, 0))'
    jam_formula = f'=IFS(B{row_num}="S1", "07:30 - 16:30", B{row_num}="S2", "15:30 - 00:30", B{row_num}="S3", "23:30 - 08:30", B{row_num}="S12", "07:30 - 00:30", B{row_num}="S23", "15:30 - 08:30", B{row_num}="OFF", "-", B{row_num}="IS", "-", TRUE, "-")'
    open_formula = f'=COUNTIFS(\'Open Insiden\'!$C:$C, $B$3, \'Open Insiden\'!$A:$A, A{row_num}&"*")'
    closed_formula = f'=COUNTIFS(\'Closed Insiden\'!$C:$C, $B$3, \'Closed Insiden\'!$A:$A, A{row_num}&"*")'
    remark_formula = f'=IFS(B{row_num}="OFF", "OFF", B{row_num}="IS", "Izin Sakit", B{row_num}="S1", "Shift 1 (Pagi)", B{row_num}="S2", "Shift 2 (Sore)", B{row_num}="S3", "Shift 3 (Malam)", B{row_num}="S12", "Shift 1 & 2", B{row_num}="S23", "Shift 2 & 3", TRUE, B{row_num})'
    
    rows_to_append.append([
        date_str,
        shift_formula,
        jam_formula,
        open_formula,
        closed_formula,
        remark_formula
    ])

print(f"2. Appending {len(rows_to_append)} rows to Summary sheet...")
for idx, r in enumerate(rows_to_append):
    res = kirim_perintah({'action': 'append', 'id': TIMESHEET_SS_ID, 'tab_name': 'Summary', 'row': r})
    if idx % 10 == 0:
        print(f"  Appended row {idx+1}/{len(rows_to_append)}...")

print("Done! Verifying read...")
data = baca_data(TIMESHEET_SS_ID, 'Summary')
print("Total rows read back:", len(data))
print("Sample row 3 (Consultant selector):", data[2] if len(data) > 2 else None)
print("Sample row 6 (Stats):", data[5] if len(data) > 5 else None)
print("Sample row 11 (Day 1 preview):", data[10] if len(data) > 10 else None)
