#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sheets_adapter

ss_id = sheets_adapter._resolve_ss_id(None)

# Put float 1.2 into Z1
sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': 'Z1', 'value': 1.2})

tests = [
    ('Z2', '=IF(OR(Z1=1+2/10; Z1="1.2"; Z1="1,2"); "MATCH_OR"; "NO_MATCH")'),
    ('Z3', '=IF(Z1=1+2/10; "MATCH_FLOAT"; "NO_MATCH")'),
    ('Z4', '=IF(OR(ROUND(Z1*10; 0)=12; Z1="1.2"; Z1="1,2"); "MATCH_ROUND"; "NO_MATCH")')
]

for rng, val in tests:
    sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': rng, 'value': val})

d = sheets_adapter.baca_data(ss_id, 'Summary')
print('Z1 value:', repr(d[0][25] if len(d[0]) > 25 else 'N/A'))
print('Z2 (OR 1+2/10):', d[1][25] if len(d[1]) > 25 else 'N/A')
print('Z3 (Z1=1+2/10):', d[2][25] if len(d[2]) > 25 else 'N/A')
print('Z4 (OR ROUND*10=12):', d[3][25] if len(d[3]) > 25 else 'N/A')

for rng in ('Z1', 'Z2', 'Z3', 'Z4'):
    sheets_adapter.kirim_perintah({'action': 'update', 'id': ss_id, 'tab_name': 'Summary', 'range': rng, 'value': ''})
