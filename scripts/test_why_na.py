#!/usr/bin/env python3
"""
Test why QUERY returns #N/A on FILTER array
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing QUERY vs UNIQUE/COUNTIF in Y1:Y5...")
    cond = '(\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = TEXT($I$11; "DD/MM/YYYY")) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) < TIME(15;0;0))'
    
    # 1. Direct FILTER (should output 'UNCONFIRM' in Y1)
    update_cell('Y1', f'=FILTER(\'Open Insiden\'!$B$2:$B; {cond})')
    # 2. QUERY over FILTER with Col1
    update_cell('Z1', f'=QUERY(FILTER(\'Open Insiden\'!$B$2:$B; {cond}); "SELECT Col1, COUNT(Col1) GROUP BY Col1")')
    # 3. QUERY over {FILTER} with Col1
    update_cell('AA1', f'=QUERY({{FILTER(\'Open Insiden\'!$B$2:$B; {cond})}}; "SELECT Col1, COUNT(Col1) GROUP BY Col1")')
    
    time.sleep(4)
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    print(f"Y1 (FILTER sample): {repr(data[0][24]) if len(data)>0 and len(data[0])>24 else 'N/A'}")
    print(f"Y2 (FILTER sample 2): {repr(data[1][24]) if len(data)>1 and len(data[1])>24 else 'N/A'}")
    print(f"Z1 (QUERY sample): {repr(data[0][25]) if len(data)>0 and len(data[0])>25 else 'N/A'}")
    print(f"Z2 (QUERY sample 2): {repr(data[1][25]) if len(data)>1 and len(data[1])>25 else 'N/A'}")
    print(f"AA1 (QUERY {{FILTER}} sample): {repr(data[0][26]) if len(data)>0 and len(data[0])>26 else 'N/A'}")
    
    update_cell('Y1:AC40', '')

if __name__ == '__main__':
    main()
