#!/usr/bin/env python3
"""
deploy_ringkasan_to_sheets.py
------------------------------
Deploy tab 'Ringkasan' langsung ke Google Sheets live via Apps Script Web App.

Menulis:
1. Summary header + formula (Total Open/Closed Tiket, Hari Kerja, Hari Off)
2. Tabel harian (Tanggal, Shift, Jam, Open, Closed, Remark) — 30 hari
3. Nama Petugas dropdown area

Menggunakan Apps Script actions: add_tab, update, append
"""

import json
import urllib.request
import urllib.parse
import sys
import os
import time

# ── Pastikan bisa import dari project ──
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config import settings

WEB_APP_URL = settings.web_app_url
SS_ID = settings.timesheet_ss_id

# ── Config bulan ──
MONTH = 6       # Juni
YEAR = 2026
NUM_DAYS = 30   # Juni = 30 hari

# Baris karyawan di Jadwal Shifting: row 3 sampai row 17 (15 orang)
SCHED_FIRST_ROW = 3
SCHED_LAST_ROW = 17

TAB_NAME = 'Ringkasan'


def kirim(payload):
    """Send POST to Apps Script."""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(WEB_APP_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {'status': 'error', 'message': str(e)}


def update_cell(range_str, value):
    """Update single cell/range."""
    return kirim({
        'action': 'update',
        'id': SS_ID,
        'tab_name': TAB_NAME,
        'range': range_str,
        'value': value
    })


def update_batch(updates):
    """Update multiple cells sequentially with progress."""
    total = len(updates)
    for i, (range_str, value) in enumerate(updates):
        result = update_cell(range_str, value)
        if (i + 1) % 10 == 0 or i == total - 1:
            print(f"  [{i+1}/{total}] Updated {range_str}")
        if result.get('status') != 'success':
            print(f"  [WARNING] Failed to update {range_str}: {result}")


def get_col_letter(n):
    """1-based column number to letter(s)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════
print(f"🎯 Deploying tab '{TAB_NAME}' ke Google Sheets: {SS_ID}")
print(f"   Bulan: Juni {YEAR} ({NUM_DAYS} hari)")
print()

# ── Step 1: Buat tab baru (atau akan pakai existing jika sudah ada) ──
print("📋 Step 1: Membuat tab Ringkasan...")
result = kirim({
    'action': 'add_tab',
    'id': SS_ID,
    'tab_name': TAB_NAME
})
print(f"  Result: {result}")

# Clear dulu isi tab (jika sudah ada data lama)
print("  Clearing existing content...")
kirim({
    'action': 'clear',
    'id': SS_ID,
    'tab_name': TAB_NAME
})

# ── Step 2: Siapkan semua cell updates ────────────────────────────────
print()
print("📝 Step 2: Menyiapkan rumus...")

updates = []

# ── ROW 1: Summary Headers ──
updates.append(('A1', 'Total Open Tiket'))
updates.append(('C1', 'Total Closed Tiket'))
updates.append(('E1', 'Hari Kerja'))
updates.append(('G1', 'Hari Off'))

# Data table starts at row 5 (header) → data rows 6 to 6+NUM_DAYS-1
DATA_HEADER_ROW = 5
DATA_START_ROW = 6
DATA_END_ROW = DATA_START_ROW + NUM_DAYS - 1  # row 35

# ── ROW 2: Summary Formulas ──
# Total Open Tiket = SUM kolom D
updates.append(('A2', f'=SUM(D{DATA_START_ROW}:D{DATA_END_ROW})'))
# Total Closed Tiket = SUM kolom E
updates.append(('C2', f'=SUM(E{DATA_START_ROW}:E{DATA_END_ROW})'))
# Hari Kerja = shift yang bukan OFF dan bukan IS
updates.append(('E2', f'=COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"<>OFF")-COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"IS")-COUNTBLANK(B{DATA_START_ROW}:B{DATA_END_ROW})'))
# Hari Off
updates.append(('G2', f'=COUNTIF(B{DATA_START_ROW}:B{DATA_END_ROW},"OFF")'))

# ── ROW 3: Spacer (kosong) ──

# ── ROW 4: Nama Petugas label + value ──
updates.append(('H4', 'Nama Petugas'))

# ── ROW 5: Table Headers ──
updates.append(('A5', 'Tanggal'))
updates.append(('B5', 'Shift'))
updates.append(('C5', 'Jam'))
updates.append(('D5', 'Open'))
updates.append(('E5', 'Closed'))
updates.append(('F5', 'Remark'))

# ── ROW 5: Nama Petugas dropdown placeholder ──
# Di Google Sheets, Data Validation tidak bisa di-set via Apps Script update
# Jadi kita tulis nama default dulu, user bisa set dropdown manual
updates.append(('H5', 'Achmad Rizki Santoso'))

# ── ROWs 6 to 35: Data rows with formulas ────────────────────────────
for day in range(1, NUM_DAYS + 1):
    row = DATA_START_ROW + day - 1
    sched_col = get_col_letter(day + 1)  # day 1 → B, day 2 → C, etc.

    # A: Tanggal
    date_str = f"{day:02d}/{MONTH:02d}/{YEAR}"
    updates.append((f'A{row}', date_str))

    # B: Shift — INDEX/MATCH dari Jadwal Shifting
    shift_formula = (
        f"=IFERROR(INDEX('Jadwal Shifting'!{sched_col}${SCHED_FIRST_ROW}:{sched_col}${SCHED_LAST_ROW},"
        f"MATCH($H$5,'Jadwal Shifting'!$A${SCHED_FIRST_ROW}:$A${SCHED_LAST_ROW},0)),\"\")"
    )
    updates.append((f'B{row}', shift_formula))

    # C: Jam — berdasarkan shift (dari config.py)
    jam_formula = (
        f'=IF(B{row}="1","06:00 — 15:00",'
        f'IF(B{row}="2","14:00 — 23:00",'
        f'IF(B{row}="3","22:00 — 07:00",'
        f'IF(B{row}="1.2","06:00 — 23:00",'
        f'IF(B{row}="2.3","14:00 — 07:00",'
        f'"")))))'
    )
    updates.append((f'C{row}', jam_formula))

    # D: Open Ticket
    # Tanggal di Open Insiden adalah TEXT format "DD/MM/YYYY H:MM"
    # Gunakan LEFT + TEXT matching: LEFT(A_col, 10) = "DD/MM/YYYY"
    # Atau gunakan DATEVALUE pada text — tapi lebih reliable pakai text match
    date_pattern = f"{day:02d}/{MONTH:02d}/{YEAR}"
    open_formula = (
        f'=IF(OR(B{row}="OFF",B{row}="IS",B{row}=""),"",'
        f'COUNTIFS('
        f"'Open Insiden'!$C:$C,$H$5,"
        f"'Open Insiden'!$A:$A,\"{date_pattern}*\""
        f'))'
    )
    updates.append((f'D{row}', open_formula))

    # E: Closed Ticket
    closed_formula = (
        f'=IF(OR(B{row}="OFF",B{row}="IS",B{row}=""),"",'
        f'COUNTIFS('
        f"'Closed Insiden'!$C:$C,$H$5,"
        f"'Closed Insiden'!$A:$A,\"{date_pattern}*\""
        f'))'
    )
    updates.append((f'E{row}', closed_formula))

    # F: Remark
    remark_formula = (
        f'=IF(B{row}="OFF","OFF",'
        f'IF(B{row}="IS","Izin Sakit",'
        f'IF(B{row}="1","Shift 1",'
        f'IF(B{row}="2","Shift 2",'
        f'IF(B{row}="3","Shift 3",'
        f'IF(B{row}="1.2","Shift 1&2",'
        f'IF(B{row}="2.3","Shift 2&3",'
        f'"")))))))' 
    )
    updates.append((f'F{row}', remark_formula))

print(f"  Total cell updates: {len(updates)}")

# ── Step 3: Deploy ke Google Sheets ──────────────────────────────────
print()
print("🚀 Step 3: Mengirim ke Google Sheets...")
update_batch(updates)

print()
print("✅ Selesai!")
print(f"   Tab '{TAB_NAME}' sudah ada di Google Sheets")
print(f"   URL: https://docs.google.com/spreadsheets/d/{SS_ID}")
print()
print("📋 Yang perlu dilakukan manual di Google Sheets:")
print("   1. Set Data Validation (dropdown) di sel H5:")
print(f"      Range sumber: 'Jadwal Shifting'!A{SCHED_FIRST_ROW}:A{SCHED_LAST_ROW}")
print("   2. Format kolom/warna sesuai selera (opsional)")
print("   3. Ganti nama di H5 → semua data otomatis berubah")
