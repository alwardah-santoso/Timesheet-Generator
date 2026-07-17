#!/usr/bin/env python3
"""
Test FILTER row counts directly inside Google Sheets
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing FILTER row counts in Y1:Y4...")
    # Just filter by petugas
    update_cell('Y1', '=IFERROR(ROWS(FILTER(\'Open Insiden\'!$B$2:$B; \'Open Insiden\'!$C$2:$C = $P$11)); 0)')
    # Filter by petugas + date
    update_cell('Y2', '=IFERROR(ROWS(FILTER(\'Open Insiden\'!$B$2:$B; (\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = TEXT($I$11; "DD/MM/YYYY")))); 0)')
    # Filter by petugas + date + time >= 6
    update_cell('Y3', '=IFERROR(ROWS(FILTER(\'Open Insiden\'!$B$2:$B; (\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = TEXT($I$11; "DD/MM/YYYY")) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) >= TIME(6;0;0)))); 0)')
    # Full cond_s1
    update_cell('Y4', '=IFERROR(ROWS(FILTER(\'Open Insiden\'!$B$2:$B; (\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = TEXT($I$11; "DD/MM/YYYY")) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) < TIME(15;0;0)))); 0)')
    
    time.sleep(3)
    
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    for i in range(4):
        val = data[i][24] if len(data) > i and len(data[i]) > 24 else 'N/A'
        print(f"Y{i+1}: {repr(val)}")
        
    update_cell('Y1:Y4', '')

if __name__ == '__main__':
    main()
