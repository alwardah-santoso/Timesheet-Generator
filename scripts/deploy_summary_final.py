#!/usr/bin/env python3
"""
deploy_summary_final.py
-----------------------
Deploy rumus dinamis ke tab 'Summary' di Google Sheets live.
Khusus memperbarui rentang B12:G41 (30 hari bulan Juni 2026) dengan filter jam shift yang akurat,
serta mengacu pada sel nama petugas di $J$11.

Fitur Logika Waktu:
- Shift 1 (1 / "1"): 06:00 s.d. 15:00 hari H
- Shift 2 (2 / "2"): 14:00 s.d. 23:00 hari H
- Shift 3 (3 / "3"): 22:00 hari H s.d. 07:00 hari H+1
- Shift 1.2 ("1.2"): 06:00 s.d. 23:00 hari H
- Shift 2.3 ("2.3"): 14:00 hari H s.d. 07:00 hari H+1

Menggunakan SUMPRODUCT + IFERROR(TIMEVALUE(MID(...))) untuk memparsing string timestamp
DD/MM/YYYY HH:MM di kolom A pada Open Insiden dan Closed Insiden secara akurat di locale Indonesia (id_ID).
"""

import json
import urllib.request
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config import settings

WEB_APP_URL = settings.web_app_url
SS_ID = settings.timesheet_ss_id

MONTH = 6
YEAR = 2026
NUM_DAYS = 30

SCHED_FIRST_ROW = 3
SCHED_LAST_ROW = 17

TAB_NAME = 'Summary'
START_ROW = 12


def kirim(payload, retries=3):
    data = json.dumps(payload).encode('utf-8')
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(WEB_APP_URL, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode('utf-8')
                result = json.loads(raw)
                if isinstance(result, dict) and result.get('status') == 'success':
                    return result
                elif isinstance(result, dict):
                    if attempt == retries:
                        return result
                else:
                    if attempt == retries:
                        return {'status': 'success_redirected', 'raw': str(result)[:100]}
        except Exception as e:
            if attempt == retries:
                print(f"  [ERROR] after {retries} attempts: {e}")
                return {'status': 'error', 'message': str(e)}
        time.sleep(1.5 * attempt)
    return {'status': 'error', 'message': 'Max retries reached'}


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
        if not isinstance(result, dict) or (result.get('status') != 'success' and result.get('status') != 'success_redirected'):
            print(f"  [WARNING] Failed {range_str}: {result}")


def col_letter(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


print(f"🎯 Deploy rumus akurat ke tab '{TAB_NAME}' (Baris 12 - 41)")
print(f"   SS_ID: {SS_ID}")
print(f"   Mengacu pada Nama Petugas di: $J$11")
print()

updates = []

for day in range(1, NUM_DAYS + 1):
    row = START_ROW + day - 1
    sched_col = col_letter(day + 1)  # day 1 → B, day 2 → C

    # Tanggal H dan H+1 string DD/MM/YYYY
    d_curr = datetime(YEAR, MONTH, day)
    d_next = d_curr + timedelta(days=1)
    date_str = d_curr.strftime('%d/%m/%Y')
    next_date_str = d_next.strftime('%d/%m/%Y')

    # B: Tanggal
    updates.append((f'B{row}', f'=DATE({YEAR}; {MONTH}; {day})'))

    # C: Shift — INDEX/MATCH mengacu $J$11
    shift_formula = (
        f"=IFERROR(INDEX('Jadwal Shifting'!{sched_col}${SCHED_FIRST_ROW}:{sched_col}${SCHED_LAST_ROW}; "
        f"MATCH($J$11; 'Jadwal Shifting'!$A${SCHED_FIRST_ROW}:$A${SCHED_LAST_ROW}; 0)); \"\")"
    )
    updates.append((f'C{row}', shift_formula))

    # D: Jam Kerja
    jam_formula = (
        f'=IF(OR(C{row}=1; C{row}="1"); "06:00 — 15:00"; '
        f'IF(OR(C{row}=2; C{row}="2"); "14:00 — 23:00"; '
        f'IF(OR(C{row}=3; C{row}="3"); "22:00 — 07:00"; '
        f'IF(C{row}="1.2"; "06:00 — 23:00"; '
        f'IF(C{row}="2.3"; "14:00 — 07:00"; '
        f'\"\")))))'
    )
    updates.append((f'D{row}', jam_formula))

    # Helper function to build SUMPRODUCT string for a sheet ('Open Insiden' or 'Closed Insiden')
    def get_ticket_formula(sheet_name):
        s1 = (
            f'SUMPRODUCT(({sheet_name}!$C$2:$C$6000=$J$11) * '
            f'(LEFT({sheet_name}!$A$2:$A$6000; 10)="{date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) >= TIME(6;0;0)) * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) < TIME(15;0;0)))'
        )
        s2 = (
            f'SUMPRODUCT(({sheet_name}!$C$2:$C$6000=$J$11) * '
            f'(LEFT({sheet_name}!$A$2:$A$6000; 10)="{date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) >= TIME(14;0;0)) * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) < TIME(23;0;0)))'
        )
        s3 = (
            f'SUMPRODUCT(({sheet_name}!$C$2:$C$6000=$J$11) * ('
            f'((LEFT({sheet_name}!$A$2:$A$6000; 10)="{date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) >= TIME(22;0;0))) + '
            f'((LEFT({sheet_name}!$A$2:$A$6000; 10)="{next_date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) < TIME(7;0;0)))'
            f'))'
        )
        s12 = (
            f'SUMPRODUCT(({sheet_name}!$C$2:$C$6000=$J$11) * '
            f'(LEFT({sheet_name}!$A$2:$A$6000; 10)="{date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) >= TIME(6;0;0)) * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) < TIME(23;0;0)))'
        )
        s23 = (
            f'SUMPRODUCT(({sheet_name}!$C$2:$C$6000=$J$11) * ('
            f'((LEFT({sheet_name}!$A$2:$A$6000; 10)="{date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) >= TIME(14;0;0))) + '
            f'((LEFT({sheet_name}!$A$2:$A$6000; 10)="{next_date_str}") * '
            f'(IFERROR(TIMEVALUE(MID({sheet_name}!$A$2:$A$6000; 12; 5)); 0) < TIME(7;0;0)))'
            f'))'
        )
        return (
            f'=IF(OR(C{row}="OFF"; ISNUMBER(SEARCH("IS"; C{row})); C{row}=""); ""; '
            f'IF(OR(C{row}=1; C{row}="1"); {s1}; '
            f'IF(OR(C{row}=2; C{row}="2"); {s2}; '
            f'IF(OR(C{row}=3; C{row}="3"); {s3}; '
            f'IF(C{row}="1.2"; {s12}; '
            f'IF(C{row}="2.3"; {s23}; '
            f'\"\"))))))'
        )

    # E: Open Ticket
    updates.append((f'E{row}', get_ticket_formula('\'Open Insiden\'')))

    # F: Closed Ticket
    updates.append((f'F{row}', get_ticket_formula('\'Closed Insiden\'')))

    # G: Remark
    remark_formula = (
        f'=IF(C{row}="OFF"; "OFF"; '
        f'IF(ISNUMBER(SEARCH("IS"; C{row})); "Izin Sakit"; '
        f'IF(OR(C{row}=1; C{row}="1"); "Shift 1"; '
        f'IF(OR(C{row}=2; C{row}="2"); "Shift 2"; '
        f'IF(OR(C{row}=3; C{row}="3"); "Shift 3"; '
        f'IF(C{row}="1.2"; "Shift 1&2"; '
        f'IF(C{row}="2.3"; "Shift 2&3"; '
        f'\"\")))))))'
    )
    updates.append((f'G{row}', remark_formula))

print(f"  Total sel yang akan diupdate: {len(updates)} (B12:G41)")
print()
print("🚀 Mengirim update ke Google Sheets...")
update_batch(updates)

print()
print("✅ Deploy selesai!")
