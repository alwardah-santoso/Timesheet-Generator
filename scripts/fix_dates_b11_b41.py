import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

colLetters = ["B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE","AF"]

for r in range(11, 42):
    cLet = colLetters[r - 11]
    formula = f"=DATE(2026; 7; 'Jadwal Shifting'!{cLet}$1)"
    
    res = kirim_perintah({
        'action': 'update',
        'tab_name': 'Summary',
        'range': f'B{r}',
        'value': formula
    })
    print(f"Update B{r}: {res.get('status')}")
