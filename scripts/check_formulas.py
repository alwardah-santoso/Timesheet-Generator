import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

res = kirim_perintah({
    'action': 'get_formulas',
    'tab_name': 'Summary',
    'range': 'B46:B47'
})
print(json.dumps(res, indent=2))
