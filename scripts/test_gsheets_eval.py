#!/usr/bin/env python3
"""
Test exact Google Sheets formula evaluations in Y1:Y8 on Summary tab
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing formula components in Y1:Y8...")
    update_cell('Y1', '=TEXT($I$11; "DD/MM/YYYY")')
    update_cell('Y2', '=TEXT($I$11; "dd/mm/yyyy")')
    update_cell('Y3', '=TEXT($I$11; "dd/mm/rrrr")')
    update_cell('Y4', '=VLOOKUP($I$11; $B$12:$C$41; 2; FALSE)')
    update_cell('Y5', '=LEFT(\'Open Insiden\'!$A$2; 10)')
    update_cell('Y6', '=MID(\'Open Insiden\'!$A$2; 12; 5)')
    update_cell('Y7', '=IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2; 12; 5)); "TIME_ERR")')
    update_cell('Y8', '=COUNTIF(\'Open Insiden\'!$C$2:$C; $P$11)')
    
    time.sleep(2)  # Wait for calculation
    
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    for i in range(8):
        val = data[i][24] if len(data) > i and len(data[i]) > 24 else 'N/A'
        print(f"Y{i+1}: {repr(val)}")
        
    print("Cleaning up Y1:Y8...")
    update_cell('Y1:Y8', '')

if __name__ == '__main__':
    main()
