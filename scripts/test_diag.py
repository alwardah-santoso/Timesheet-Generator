#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sheets_adapter

ss_id = sheets_adapter._resolve_ss_id(None)

# Test FILTER + ROWS with IFERROR(TIMEVALUE)
f1 = '=IFERROR(ROWS(FILTER(\'Open Insiden\'!$C$2:$C$6000; (\'Open Insiden\'!$C$2:$C$6000="Achmad Rizki Santoso") * (LEFT(\'Open Insiden\'!$A$2:$A$6000; 10)="01/06/2026") * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A$6000; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A$6000; 12; 5)); 0) < TIME(15;0;0)))); 0)'

# Test SUMPRODUCT with IFERROR(TIMEVALUE) and exact text left
f2 = '=SUMPRODUCT((\'Open Insiden\'!$C$2:$C$6000="Achmad Rizki Santoso") * (LEFT(\'Open Insiden\'!$A$2:$A$6000; 10)="01/06/2026") * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A$6000; 12; 5)); 0) >= TIME(6;0;0)) * (IFERROR(TIMEVALUE(MID(\'Open Insiden\'!$A$2:$A$6000; 12; 5)); 0) < TIME(15;0;0)))'

# Test wildcard COUNTIFS sum for Shift 1 (hours 6 to 14)
f3 = '=COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 6:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 06:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 7:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 07:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 8:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 08:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 9:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 09:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 10:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 11:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 12:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 13:*") + COUNTIFS(\'Open Insiden\'!$C:$C; "Achmad Rizki Santoso"; \'Open Insiden\'!$A:$A; "01/06/2026 14:*")'

sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z1', 'value': f1})
sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z2', 'value': f2})
sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z3', 'value': f3})

d = sheets_adapter.baca_data(ss_id, 'Summary')
print('Z1 (FILTER + ROWS):', d[0][25] if len(d[0]) > 25 else 'N/A')
print('Z2 (SUMPRODUCT):', d[1][25] if len(d[1]) > 25 else 'N/A')
print('Z3 (wildcard sum of hours 6..14):', d[2][25] if len(d[2]) > 25 else 'N/A')

sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z1', 'value': ''})
sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z2', 'value': ''})
sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z3', 'value': ''})
