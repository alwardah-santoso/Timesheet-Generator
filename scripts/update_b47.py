import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

r = 47
fB = f"=IF(OR(A{r}=\"\", $C$4=\"\"), \"\", INDEX('Jadwal Shifting'!$B$2:$AF$50, MATCH($C$4, 'Jadwal Shifting'!$A$2:$A$50, 0), MATCH(DAY(A{r}), 'Jadwal Shifting'!$B$1:$AF$1, 0)))"

res = kirim_perintah({
    'action': 'update',
    'tab_name': 'Summary',
    'range': f'B{r}',
    'value': fB
})
print("Update B47:", res)

# Also might as well update the rest of row 47 and the KPI if the user wanted it
# Let's just update B47 first to see if it works.
