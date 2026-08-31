import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

fB = "=IF(OR(A47=\"\"; $C$4=\"\"); \"\"; INDEX('Jadwal Shifting'!$B$2:$AF$50; MATCH($C$4; 'Jadwal Shifting'!$A$2:$A$50; 0); MATCH(DAY(A47); 'Jadwal Shifting'!$B$1:$AF$1; 0)))"

res = kirim_perintah({
    'action': 'update',
    'tab_name': 'Summary',
    'range': 'B47',
    'value': fB
})
print("Update B47:", res)
