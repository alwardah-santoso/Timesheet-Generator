#!/usr/bin/env python3
"""
Verify live values in J12:M20 after deployment
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    print("Live values in drill-down table (Rows 12-18):")
    for i in range(11, 18):
        if i < len(data):
            row = data[i]
            j = row[9] if len(row) > 9 else ''
            k = row[10] if len(row) > 10 else ''
            l = row[11] if len(row) > 11 else ''
            m = row[12] if len(row) > 12 else ''
            print(f"Row {i+1}: J={repr(j)} | K={repr(k)} | L={repr(l)} | M={repr(m)}")

if __name__ == '__main__':
    main()
