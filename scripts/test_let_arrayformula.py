#!/usr/bin/env python3
"""
Test LET with ARRAYFORMULA on intermediate range variables
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scripts.deploy_incident_breakdown import update_cell
from sheets_adapter import baca_data, TIMESHEET_SS_ID

def main():
    print("Testing LET with ARRAYFORMULA on dt_date and dt_time in Y1:Y4...")
    
    # Clean Y1:AC15
    update_cell('Y1:AC15', '')
    
    # 1. Test cond_s1 with ARRAYFORMULA around dt_date and dt_time inside LET
    formula_af = (
        '=LET('
        '  tgl; TEXT($I$11; "DD/MM/YYYY");'
        '  A; \'Open Insiden\'!$A$2:$A;'
        '  B; \'Open Insiden\'!$B$2:$B;'
        '  C; \'Open Insiden\'!$C$2:$C;'
        '  dt_date; ARRAYFORMULA(LEFT(A; 10));'
        '  dt_time; ARRAYFORMULA(IFERROR(TIMEVALUE(MID(A; 12; 5)); 0));'
        '  is_petugas; ARRAYFORMULA(C = $P$11);'
        '  cond_s1; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)));'
        '  ROWS(FILTER(B; cond_s1))'
        ')'
    )
    update_cell('Y1', formula_af)
    
    # 2. Test full QUERY + FILTER with ARRAYFORMULA variables in Z1
    formula_full = (
        '=LET('
        '  shift; IFERROR(VLOOKUP($I$11; $B$12:$C$41; 2; FALSE); "OFF");'
        '  tgl; TEXT($I$11; "DD/MM/YYYY");'
        '  tgl_next; TEXT($I$11+1; "DD/MM/YYYY");'
        '  A; \'Open Insiden\'!$A$2:$A;'
        '  B; \'Open Insiden\'!$B$2:$B;'
        '  C; \'Open Insiden\'!$C$2:$C;'
        '  dt_date; ARRAYFORMULA(LEFT(A; 10));'
        '  dt_time; ARRAYFORMULA(IFERROR(TIMEVALUE(MID(A; 12; 5)); 0));'
        '  is_petugas; ARRAYFORMULA(C = $P$11);'
        '  cond_s1; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(15;0;0)));'
        '  cond_s2; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(14;0;0)) * (dt_time < TIME(23;0;0)));'
        '  cond_s3; ARRAYFORMULA(is_petugas * (((dt_date = tgl) * (dt_time >= TIME(22;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0)))));'
        '  cond_s12; ARRAYFORMULA(is_petugas * (dt_date = tgl) * (dt_time >= TIME(6;0;0)) * (dt_time < TIME(23;0;0)));'
        '  cond_s23; ARRAYFORMULA(is_petugas * (((dt_date = tgl) * (dt_time >= TIME(14;0;0))) + ((dt_date = tgl_next) * (dt_time < TIME(7;0;0)))));'
        '  filtered_B; IF(OR(shift=1; shift="1"); FILTER(B; cond_s1);'
        '              IF(OR(shift=2; shift="2"); FILTER(B; cond_s2);'
        '              IF(OR(shift=3; shift="3"); FILTER(B; cond_s3);'
        '              IF(OR(shift=1+2/10; shift="1.2"; shift="1,2"); FILTER(B; cond_s12);'
        '              IF(OR(shift=2+3/10; shift="2.3"; shift="2,3"); FILTER(B; cond_s23);'
        '              "")))));'
        '  QUERY(filtered_B; "SELECT Col1, COUNT(Col1) GROUP BY Col1 LABEL Col1 \'\', COUNT(Col1) \'\'"; 0)'
        ')'
    )
    update_cell('Z1', formula_full)

    time.sleep(4)
    data = baca_data(TIMESHEET_SS_ID, 'Summary')
    
    print("Y1 (ROWS with ARRAYFORMULA):", repr(data[0][24]) if len(data)>0 and len(data[0])>24 else 'N/A')
    for i in range(5):
        val_z = data[i][25] if len(data) > i and len(data[i]) > 25 else 'N/A'
        val_aa = data[i][26] if len(data) > i and len(data[i]) > 26 else 'N/A'
        print(f"Row {i+1}: Z={repr(val_z)}, AA={repr(val_aa)}")
        
    update_cell('Y1:AC15', '')

if __name__ == '__main__':
    main()
