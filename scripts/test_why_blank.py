#!/usr/bin/env python3
"""
Investigate why June 14 produces blank in J12
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    summary_data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    i11 = summary_data[10][8] if len(summary_data) > 10 and len(summary_data[10]) > 8 else ''
    p11 = summary_data[10][15] if len(summary_data) > 10 and len(summary_data[10]) > 15 else ''
    print(f"Current I11: {repr(i11)}")
    print(f"Current P11: {repr(p11)}")
    
    print("Current J12:M16 output:")
    for i, row in enumerate(summary_data[11:16]):
        print(f"  Row {i+12}: {row[9:13] if len(row) > 9 else []}")
        
    # Check shifts map for June 14
    for row in summary_data[11:41]:
        if len(row) > 2 and '2026-06-13' in str(row[1]) or '2026-06-14' in str(row[1]):
            print(f"  Shift row: date={row[1][:10]}, shift={row[2]}")

if __name__ == '__main__':
    main()
