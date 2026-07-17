#!/usr/bin/env python3
"""
Test QUERY over FILTER without IFERROR in Z1 and Z5 to see exact error string
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing QUERY syntax errors without IFERROR...")
    
    # Clean Z1:AC10 first
    update_cell('Z1:AC15', '')
    
    cond = '(\'Open Insiden\'!$C$2:$C = $P$11) * (LEFT(\'Open Insiden\'!$A$2:$A; 10) = TEXT($I$11; "DD/MM/YYYY")) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A; 12; 5)); 0) < TIME(15;0;0))'
    
    # 1. Direct QUERY(FILTER(...)) in Z1
    update_cell('Z1', f'=QUERY(FILTER(\'Open Insiden\'!$B$2:$B; {cond}); "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\'"; 0)')
    
    # 2. Exact LET formula WITHOUT IFERROR around QUERY in Z5
    let_no_iferror = (
        '=LET('
        '  shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF");'
        '  tgl; TEXT($I$11; "DD/MM/YYYY");'
        '  tgl_next; TEXT($I$11+1; "DD/MM/YYYY");'
        '  A; \'Open Insiden\'!$A$2:$A;'
        '  B; \'Open Insiden\'!$B$2:$B;'
        '  C; \'Open Insiden\'!$C$2:$C;'
        '  dt_date; LEFT(A; 10);'
        '  dt_time; IFERROR(TIMEVALUE(MID(A; 12; 5)); 0);'
        '  is_petugas; (C = $P$11);'
        '  cond_s1; is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0));'
        '  cond_s2; is_petugas * (dt_date = tgl) * (dt_time >= TIME(14;0;0)) * (dt_time < TIME(23;0;0));'
        '  cond_s3; is_petugas * (((dt_date = tgl) * (dt_time >= TIME(22;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0))));'
        '  cond_s12; is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(23;0;0));'
        '  cond_s23; is_petugas * (((dt_date = tgl) * (dt_time >= TIME(14;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0))));'
        '  filtered_B; IF(OR(shift=1; shift="1"); FILTER(B; cond_s1);'
        '              IF(OR(shift=2; shift="2"); FILTER(B; cond_s2);'
        '              IF(OR(shift=3; shift="3"); FILTER(B; cond_s3);'
        '              IF(OR(shift=1+2/10; shift="1.2"; shift="1,2"); FILTER(B; cond_s12);'
        '              IF(OR(shift=2+3/10; shift="2.3"; shift="2,3"); FILTER(B; cond_s23);'
        '              "")))));'
        '  QUERY(filtered_B; "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\', COUNT(Col1) \'\'"; 0)'
        ')'
    )
    update_cell('Z5', let_no_iferror)
    
    # Also let's check what J12 and L12 right now show on row 12
    time.sleep(4)
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    print("Z1 (Direct QUERY+FILTER):", repr(data[0][25]) if len(data)>0 and len(data[0])>25 else 'N/A')
    print("AA1 (Direct QUERY+FILTER col 2):", repr(data[0][26]) if len(data)>0 and len(data[0])>26 else 'N/A')
    print("Z5 (LET without IFERROR):", repr(data[4][25]) if len(data)>4 and len(data[4])>25 else 'N/A')
    print("AA5 (LET col 2):", repr(data[4][26]) if len(data)>4 and len(data[4])>26 else 'N/A')
    print("Current J12:", repr(data[11][9]) if len(data)>11 and len(data[11])>9 else 'N/A')
    print("Current K12:", repr(data[11][10]) if len(data)>11 and len(data[11])>10 else 'N/A')
    
    update_cell('Z1:AC15', '')

if __name__ == '__main__':
    main()
