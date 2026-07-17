#!/usr/bin/env python3
"""
Test QUERY over FILTER directly inside Google Sheets without IFERROR
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing QUERY over FILTER in Y1:Z10...")
    formula = (
        '=LET('
        '  tgl; TEXT($I$11; "DD/MM/YYYY");'
        '  B; \'Open Insiden\'!$B$2:$B;'
        '  cond; (\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = tgl) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) < TIME(15;0;0));'
        '  fb; FILTER(B; cond);'
        '  QUERY(fb; "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\'"; 0)'
        ')'
    )
    update_cell('Y1', formula)
    time.sleep(3)
    
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    for i in range(10):
        val_y = data[i][24] if len(data) > i and len(data[i]) > 24 else 'N/A'
        val_z = data[i][25] if len(data) > i and len(data[i]) > 25 else 'N/A'
        print(f"Row {i+1}: Y={repr(val_y)}, Z={repr(val_z)}")
        
    update_cell('Y1:Z20', '')

if __name__ == '__main__':
    main()
