import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

updates = [
    ('A47', ''),
    ('C47', ''),
    ('D47', ''),
    ('E47', ''),
    ('F47', '')
]

for rng, val in updates:
    res = kirim_perintah({
        'action': 'update',
        'tab_name': 'Summary',
        'range': rng,
        'value': val
    })
    print(f"Update {rng}: {res.get('status')}")
