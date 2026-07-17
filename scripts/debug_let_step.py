#!/usr/bin/env python3
"""
Debug exact steps of LET formula inside Google Sheets on June 14
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing LET intermediate steps in Y1:Y6...")
    
    # Clean Y1:AC15
    update_cell('Y1:AC15', '')
    
    # 1. What does shift evaluate to in LET?
    update_cell('Y1', '=LET(shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF"); shift)')
    
    # 2. What does tgl evaluate to?
    update_cell('Y2', '=LET(tgl; TEXT($I$11; "DD/MM/YYYY"); tgl)')
    
    # 3. What does OR(shift=1; shift="1") evaluate to?
    update_cell('Y3', '=LET(shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF"); OR(shift=1; shift="1"))')
    
    # 4. How many rows does cond_s1 match?
    update_cell('Y4', '=LET(tgl; TEXT($I$11; "DD/MM/YYYY"); A; \'Open Insiden\'!$A$2:$A; C; \'Open Insiden\'!$C$2:$C; dt_date; LEFT(A; 10); dt_time; IFERROR(TIMEVALUE(MID(A; 12; 5)); 0); is_petugas; (C = $P$11); cond_s1; is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)); IFERROR(ROWS(FILTER(\'Open Insiden\'!$B$2:$B; cond_s1)); "NO_MATCH"))')
    
    # 5. What does filtered_B return? (first item or count)
    update_cell('Y5', '=LET(shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF"); tgl; TEXT($I$11; "DD/MM/YYYY"); A; \'Open Insiden\'!$A$2:$A; B; \'Open Insiden\'!$B$2:$B; C; \'Open Insiden\'!$C$2:$C; dt_date; LEFT(A; 10); dt_time; IFERROR(TIMEVALUE(MID(A; 12; 5)); 0); is_petugas; (C = $P$11); cond_s1; is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)); filtered_B; IF(OR(shift=1; shift="1"); FILTER(B; cond_s1); "NOT_S1"); IFERROR(INDEX(filtered_B; 1; 1); "FB_ERR"))')
    
    # 6. What does QUERY(filtered_B) return?
    update_cell('Y6', '=LET(shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF"); tgl; TEXT($I$11; "DD/MM/YYYY"); A; \'Open Insiden\'!$A$2:$A; B; \'Open Insiden\'!$B$2:$B; C; \'Open Insiden\'!$C$2:$C; dt_date; LEFT(A; 10); dt_time; IFERROR(TIMEVALUE(MID(A; 12; 5)); 0); is_petugas; (C = $P$11); cond_s1; is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)); filtered_B; FILTER(B; cond_s1); IFERROR(INDEX(QUERY(filtered_B; "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\', COUNT(Col1) \'\'"; 0); 1; 1); "Q_ERR"))')

    time.sleep(4)
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    for i in range(6):
        val = data[i][24] if len(data) > i and len(data[i]) > 24 else 'N/A'
        print(f"Y{i+1}: {repr(val)}")
        
    update_cell('Y1:AC15', '')

if __name__ == '__main__':
    main()
