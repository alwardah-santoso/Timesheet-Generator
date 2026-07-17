#!/usr/bin/env python3
"""
deploy_incident_breakdown.py
----------------------------
Deploy formula breakdown insiden dinamis ke sel J12 (Open Insiden) dan L12 (Closed Insiden)
pada tab 'Summary'.

Rumus menggunakan LET + FILTER + QUERY untuk mencocokkan:
1. Petugas di $P$11
2. Tanggal di $I$11
3. Shift petugas pada tanggal tersebut di $B$12:$C$41 (1, 2, 3, 1.2, 2.3)
4. Rentang waktu yang tepat untuk masing-masing shift (termasuk lintas hari shift 3 & 2.3).
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
TAB_NAME = 'Summary'


def kirim(payload, retries=3):
    data = json.dumps(payload).encode('utf-8')
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(WEB_APP_URL, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode('utf-8')
                result = json.loads(raw)
                if isinstance(result, dict) and result.get('status') in ('success', 'success_redirected'):
                    return result
                elif isinstance(result, dict) and attempt == retries:
                    return result
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


def get_breakdown_formula(sheet_name):
    # sheet_name should be 'Open Insiden' or 'Closed Insiden'
    # In formula string we format let variables and conditions cleanly with ARRAYFORMULA
    return (
        f'=LET(\n'
        f'  shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF");\n'
        f'  tgl; TEXT($I$11; "DD/MM/YYYY");\n'
        f'  tgl_next; TEXT($I$11+1; "DD/MM/YYYY");\n'
        f'  A; \'{sheet_name}\'!$A$2:$A;\n'
        f'  B; \'{sheet_name}\'!$B$2:$B;\n'
        f'  C; \'{sheet_name}\'!$C$2:$C;\n'
        f'  dt_date; ARRAYFORMULA(LEFT(A; 10));\n'
        f'  dt_time; ARRAYFORMULA(IFERROR(TIMEVALUE(MID(A; 12; 5)); 0));\n'
        f'  is_petugas; ARRAYFORMULA(C = $P$11);\n'
        f'  \n'
        f'  cond_s1; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)));\n'
        f'  cond_s2; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(14;0;0)) * (dt_time < TIME(23;0;0)));\n'
        f'  cond_s3; ARRAYFORMULA(is_petugas * (((dt_date = tgl) * (dt_time >= TIME(22;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0)))));\n'
        f'  cond_s12; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(23;0;0)));\n'
        f'  cond_s23; ARRAYFORMULA(is_petugas * (((dt_date = tgl) * (dt_time >= TIME(14;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0)))));\n'
        f'  \n'
        f'  filtered_B; IF(OR(shift=1; shift="1"; shift="IS-1"); FILTER(B; cond_s1);\n'
        f'              IF(OR(shift=2; shift="2"; shift="IS-2"); FILTER(B; cond_s2);\n'
        f'              IF(OR(shift=3; shift="3"; shift="IS-3"); FILTER(B; cond_s3);\n'
        f'              IF(OR(shift=1+2/10; shift="1.2"; shift="1,2"; shift="IS-1.2"; shift="IS-1,2"); FILTER(B; cond_s12);\n'
        f'              IF(OR(shift=2+3/10; shift="2.3"; shift="2,3"; shift="IS-2.3"; shift="IS-2,3"); FILTER(B; cond_s23);\n'
        f'              "")))));\n'
        f'  \n'
        f'  IFERROR(QUERY(filtered_B; "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\', COUNT(Col1) \'\'"; 0); "")\n'
        f')'
    )


def main():
    print(f"🎯 Deploy Breakdown Formula (Open/Closed Insiden) ke tab '{TAB_NAME}'")
    print(f"   Spreadsheet ID: {SS_ID}")
    print()

    f_open = get_breakdown_formula('Open Insiden')
    f_closed = get_breakdown_formula('Closed Insiden')

    print("🧹 Membersihkan area spill (J13:K41, L13:M41, K12, M12) agar tidak ada #REF error...")
    update_cell('K12', '')
    update_cell('M12', '')
    update_cell('J13:K41', '')
    update_cell('L13:M41', '')

    print("🚀 Updating J12 (Open Insiden breakdown)...")
    res_open = update_cell('J12', f_open)
    print("   Result:", res_open)

    print("🚀 Updating L12 (Closed Insiden breakdown)...")
    res_closed = update_cell('L12', f_closed)
    print("   Result:", res_closed)

    if res_open.get('status') in ('success', 'success_redirected') and res_closed.get('status') in ('success', 'success_redirected'):
        print("\n✅ Semua formula berhasil di-deploy ke J12 dan L12 & area spill telah dibersihkan!")
    else:
        print("\n⚠️ Terjadi kendala saat deploy, periksa pesan di atas.")


if __name__ == '__main__':
    main()
