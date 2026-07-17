#!/usr/bin/env python3
"""
Test formula logic locally using python against live data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sheets_adapter import baca_data, TIMESHEET_SS_ID
from datetime import datetime

def test_logic():
    open_data = baca_data(TIMESHEET_SS_ID, 'Open Insiden')
    summary_data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    # Check I11 and P11 from summary_data
    i11 = summary_data[10][8] if len(summary_data) > 10 and len(summary_data[10]) > 8 else ''
    p11 = summary_data[10][15] if len(summary_data) > 10 and len(summary_data[10]) > 15 else ''
    print(f"Current I11 in sheet: {i11}")
    print(f"Current P11 in sheet: {p11}")
    
    # Map dates in B12:C41 to shifts
    shifts_by_date = {}
    for row in summary_data[11:41]:
        if len(row) > 2 and row[1]:
            # row[1] is like '2026-05-31T17:00:00.000Z'
            # Let's convert to DD/MM/YYYY
            # Note: in UTC 2026-05-31T17:00:00.000Z is 2026-06-01 00:00:00 in GMT+7
            # Or if it's string, how does TEXT(I11, "DD/MM/YYYY") work?
            dt_str = row[1][:10]
            shifts_by_date[dt_str] = row[2]
            
    print(f"Shifts map (first 5): {list(shifts_by_date.items())[:5]}")
    
    # Let's check what tickets exist for P11 across all dates
    tickets_for_petugas = {}
    for row in open_data[1:]:
        if len(row) > 2 and row[2] == p11:
            dt_raw = row[0] # e.g. '14/06/2026 14:18'
            dt_date = dt_raw[:10]
            dt_time_str = dt_raw[11:16]
            tickets_for_petugas.setdefault(dt_date, []).append((dt_time_str, row[1]))
            
    print(f"\nTotal dates with tickets for '{p11}' in Open Insiden: {len(tickets_for_petugas)}")
    for dt_date, t_list in sorted(tickets_for_petugas.items()):
        print(f"  Date {dt_date}: {len(t_list)} tickets (sample time: {t_list[0][0]}, sample name: {t_list[0][1]})")

if __name__ == '__main__':
    test_logic()
