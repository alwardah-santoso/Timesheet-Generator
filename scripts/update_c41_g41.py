import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

r = 41

fC = f"=IF(OR(B{r}=\"\"; $C$4=\"\"); \"\"; INDEX('Jadwal Shifting'!$B$2:$AF$50; MATCH($C$4; 'Jadwal Shifting'!$A$2:$A$50; 0); MATCH(DAY(B{r}); 'Jadwal Shifting'!$B$1:$AF$1; 0)))"
fD = f"=IFERROR(IFS(C{r}=\"1\"; \"06:00 — 15:00\"; C{r}=\"2\"; \"14:00 — 23:00\"; C{r}=\"3\"; \"22:00 — 07:00\"; C{r}=\"1.2\"; \"06:00 — 23:00\"; C{r}=\"2.3\"; \"14:00 — 07:00\"; TRUE; \"-\"); \"-\")"
fE = f"=IFERROR(IFS(OR(C{r}=\"OFF\"; LEFT(C{r};2)=\"IS\"; C{r}=\"\"); \"-\"; C{r}=\"1\"; COUNTIFS('Open Insiden'!$A:$A; \">=\" & (B{r} + TIME(6;0;0)); 'Open Insiden'!$A:$A; \"<\" & (B{r} + TIME(15;0;0))); C{r}=\"2\"; COUNTIFS('Open Insiden'!$A:$A; \">=\" & (B{r} + TIME(14;0;0)); 'Open Insiden'!$A:$A; \"<\" & (B{r} + TIME(23;0;0))); C{r}=\"3\"; COUNTIFS('Open Insiden'!$A:$A; \">=\" & (B{r} + TIME(22;0;0)); 'Open Insiden'!$A:$A; \"<\" & (B{r} + 1 + TIME(7;0;0))); C{r}=\"1.2\"; COUNTIFS('Open Insiden'!$A:$A; \">=\" & (B{r} + TIME(6;0;0)); 'Open Insiden'!$A:$A; \"<\" & (B{r} + TIME(23;0;0))); C{r}=\"2.3\"; COUNTIFS('Open Insiden'!$A:$A; \">=\" & (B{r} + TIME(14;0;0)); 'Open Insiden'!$A:$A; \"<\" & (B{r} + 1 + TIME(7;0;0))); TRUE; 0); \"-\")"
fF = f"=IFERROR(IFS(OR(C{r}=\"OFF\"; LEFT(C{r};2)=\"IS\"; C{r}=\"\"); \"-\"; C{r}=\"1\"; COUNTIFS('Closed Insiden'!$A:$A; \">=\" & (B{r} + TIME(6;0;0)); 'Closed Insiden'!$A:$A; \"<\" & (B{r} + TIME(15;0;0))); C{r}=\"2\"; COUNTIFS('Closed Insiden'!$A:$A; \">=\" & (B{r} + TIME(14;0;0)); 'Closed Insiden'!$A:$A; \"<\" & (B{r} + TIME(23;0;0))); C{r}=\"3\"; COUNTIFS('Closed Insiden'!$A:$A; \">=\" & (B{r} + TIME(22;0;0)); 'Closed Insiden'!$A:$A; \"<\" & (B{r} + 1 + TIME(7;0;0))); C{r}=\"1.2\"; COUNTIFS('Closed Insiden'!$A:$A; \">=\" & (B{r} + TIME(6;0;0)); 'Closed Insiden'!$A:$A; \"<\" & (B{r} + TIME(23;0;0))); C{r}=\"2.3\"; COUNTIFS('Closed Insiden'!$A:$A; \">=\" & (B{r} + TIME(14;0;0)); 'Closed Insiden'!$A:$A; \"<\" & (B{r} + 1 + TIME(7;0;0))); TRUE; 0); \"-\")"
fG = f"=IFERROR(IFS(C{r}=\"OFF\"; \"OFF\"; LEFT(C{r};2)=\"IS\"; \"Izin Sakit\"; C{r}=\"1\"; \"Shift 1\"; C{r}=\"2\"; \"Shift 2\"; C{r}=\"3\"; \"Shift 3\"; C{r}=\"1.2\"; \"Shift 1 & 2\"; C{r}=\"2.3\"; \"Shift 2 & 3\"; TRUE; C{r}); \"-\")"

updates = [
    (f"C{r}", fC),
    (f"D{r}", fD),
    (f"E{r}", fE),
    (f"F{r}", fF),
    (f"G{r}", fG),
]

for rng, val in updates:
    res = kirim_perintah({
        'action': 'update',
        'tab_name': 'Summary',
        'range': rng,
        'value': val
    })
    print(f"Update {rng}: {res.get('status')}")
