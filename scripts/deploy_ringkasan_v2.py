#!/usr/bin/env python3
"""
deploy_ringkasan_v2.py
-----------------------
Deploy tab 'Ringkasan' ke Google Sheets live — FIXED version.

Fixes:
- Shift values di Jadwal Shifting = angka (1, 2, 3), bukan teks ("1", "2", "3")
- Tanggal pakai =DATE() formula agar konsisten timezone
- Rumus IF comparison pakai angka, bukan string
"""

import json
import urllib.request
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config import settings

WEB_APP_URL = settings.web_app_url
SS_ID = settings.timesheet_ss_id

MONTH = 6
YEAR = 2026
NUM_DAYS = 30

SCHED_FIRST_ROW = 3
SCHED_LAST_ROW = 17

TAB_NAME = 'Ringkasan'


def kirim(payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(WEB_APP_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {'status': 'error', 'message': str(e)}


def update_cell(range_str, value):
    return kirim({
        'action': 'update',
        'id': SS_ID,
        'tab_name': TAB_NAME,
        'range': range_str,
        'value': value
    })


def update_batch(updates):
    total = len(updates)
    for i, (range_str, value) in enumerate(updates):
        result = update_cell(range_str, value)
        if (i + 1) % 10 == 0 or i == total - 1:
            print(f"  [{i+1}/{total}] Updated {range_str}")
        if result.get('status') != 'success':
            print(f"  [WARNING] Failed {range_str}: {result}")


def col_letter(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


print(f"🎯 Deploy tab '{TAB_NAME}' ke Google Sheets (v2 - FIXED)")
print(f"   SS_ID: {SS_ID}")
print(f"   Bulan: Juni {YEAR} ({NUM_DAYS} hari)")
print()

# ── Step 1: Clear tab ──
print("📋 Step 1: Clear tab Ringkasan...")
kirim({'action': 'clear', 'id': SS_ID, 'tab_name': TAB_NAME})
print("  Done")

# ── Step 2: Build updates ──
print()
print("📝 Step 2: Menyiapkan rumus (FIXED)...")

updates = []

# Layout:
# Row 1: Summary labels
# Row 2: Summary values
# Row 3: (spacer)
# Row 4: "Nama Petugas" label (H4) + dropdown value (H5)
# Row 5: Table headers
# Row 6-35: Data rows (30 hari)

DATA_HEADER_ROW = 5
DATA_START_ROW = 6
DATA_END_ROW = DATA_START_ROW + NUM_DAYS - 1  # 35

# ── ROW 1: Summary labels ──
updates.append(('A1', 'Total Open Tiket'))
updates.append(('C1', 'Total Closed Tiket'))
updates.append(('E1', 'Hari Kerja'))
updates.append(('G1', 'Hari Off'))

# ── ROW 2: Summary formulas ──
# Total Open Tiket
updates.append(('A2', f'=SUM(D{DATA_START_ROW}:D{DATA_END_ROW})'))
# Total Closed Tiket
updates.append(('C2', f'=SUM(E{DATA_START_ROW}:E{DATA_END_ROW})'))
# Hari Kerja: bukan OFF, bukan IS*, bukan kosong
# Shift bisa angka (1,2,3) atau teks ("OFF","IS-1","1.2","2.3")
updates.append(('E2',
    f'=COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"<>")'
    f'-COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"OFF")'
    f'-COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"IS*")'
))
# Hari Off
updates.append(('G2', f'=COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"OFF")'))

# ── ROW 4: Nama Petugas ──
updates.append(('H4', 'Nama Petugas'))

# ── ROW 5: Table headers ──
updates.append(('A5', 'Tanggal'))
updates.append(('B5', 'Shift'))
updates.append(('C5', 'Jam'))
updates.append(('D5', 'Open'))
updates.append(('E5', 'Closed'))
updates.append(('F5', 'Remark'))

# Nama default
updates.append(('H5', 'Achmad Rizki Santoso'))

# ── Data rows ──
for day in range(1, NUM_DAYS + 1):
    row = DATA_START_ROW + day - 1
    sched_col = col_letter(day + 1)  # day 1 → B, day 2 → C

    # A: Tanggal — pakai DATE() formula agar konsisten
    updates.append((f'A{row}', f'=DATE({YEAR},{MONTH},{day})'))

    # B: Shift — INDEX/MATCH
    shift_formula = (
        f"=IFERROR(INDEX('Jadwal Shifting'!{sched_col}${SCHED_FIRST_ROW}:{sched_col}${SCHED_LAST_ROW},"
        f"MATCH($H$5,'Jadwal Shifting'!$A${SCHED_FIRST_ROW}:$A${SCHED_LAST_ROW},0)),\"\")"
    )
    updates.append((f'B{row}', shift_formula))

    # C: Jam — shift bisa ANGKA (1,2,3) atau TEKS ("OFF","1.2","2.3","IS-1")
    # Pakai perbandingan angka DAN teks
    jam_formula = (
        f'=IF(OR(B{row}=1,B{row}="1"),"06:00 — 15:00",'
        f'IF(OR(B{row}=2,B{row}="2"),"14:00 — 23:00",'
        f'IF(OR(B{row}=3,B{row}="3"),"22:00 — 07:00",'
        f'IF(B{row}="1.2","06:00 — 23:00",'
        f'IF(B{row}="2.3","14:00 — 07:00",'
        f'"")))))'
    )
    updates.append((f'C{row}', jam_formula))

    # D: Open Ticket — COUNTIFS dengan text wildcard pada tanggal
    date_pattern = f"{day:02d}/{MONTH:02d}/{YEAR}"
    open_formula = (
        f'=IF(OR(B{row}="OFF",ISNUMBER(SEARCH("IS",B{row})),B{row}=""),"",'
        f'COUNTIFS('
        f"'Open Insiden'!$C:$C,$H$5,"
        f"'Open Insiden'!$A:$A,\"{date_pattern}*\""
        f'))'
    )
    updates.append((f'D{row}', open_formula))

    # E: Closed Ticket
    closed_formula = (
        f'=IF(OR(B{row}="OFF",ISNUMBER(SEARCH("IS",B{row})),B{row}=""),"",'
        f'COUNTIFS('
        f"'Closed Insiden'!$C:$C,$H$5,"
        f"'Closed Insiden'!$A:$A,\"{date_pattern}*\""
        f'))'
    )
    updates.append((f'E{row}', closed_formula))

    # F: Remark — handle angka DAN teks
    remark_formula = (
        f'=IF(B{row}="OFF","OFF",'
        f'IF(ISNUMBER(SEARCH("IS",B{row})),"Izin Sakit",'
        f'IF(OR(B{row}=1,B{row}="1"),"Shift 1",'
        f'IF(OR(B{row}=2,B{row}="2"),"Shift 2",'
        f'IF(OR(B{row}=3,B{row}="3"),"Shift 3",'
        f'IF(B{row}="1.2","Shift 1&2",'
        f'IF(B{row}="2.3","Shift 2&3",'
        f'"")))))))' 
    )
    updates.append((f'F{row}', remark_formula))

print(f"  Total cell updates: {len(updates)}")

# ── Step 3: Deploy ──
print()
print("🚀 Step 3: Mengirim ke Google Sheets...")
update_batch(updates)

print()
print("✅ Selesai!")
print(f"   URL: https://docs.google.com/spreadsheets/d/{SS_ID}")
