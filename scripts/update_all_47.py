import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

r = 47
# A47
cLet = "AL"
fA = f"=DATE(2026, 7, 'Jadwal Shifting'!{cLet}$1)"
# C47
fC = f"=IFERROR(IFS(B{r}=\"1\", \"06:00 — 15:00\", B{r}=\"2\", \"14:00 — 23:00\", B{r}=\"3\", \"22:00 — 07:00\", B{r}=\"1.2\", \"06:00 — 23:00\", B{r}=\"2.3\", \"14:00 — 07:00\", TRUE, \"-\"), \"-\")"
# D47
fD = f"=IFERROR(IFS(OR(B{r}=\"OFF\", LEFT(B{r},2)=\"IS\", B{r}=\"\"), \"-\", B{r}=\"1\", COUNTIFS('Open Insiden'!$A:$A, \">=\" & (A{r} + TIME(6,0,0)), 'Open Insiden'!$A:$A, \"<\" & (A{r} + TIME(15,0,0))), B{r}=\"2\", COUNTIFS('Open Insiden'!$A:$A, \">=\" & (A{r} + TIME(14,0,0)), 'Open Insiden'!$A:$A, \"<\" & (A{r} + TIME(23,0,0))), B{r}=\"3\", COUNTIFS('Open Insiden'!$A:$A, \">=\" & (A{r} + TIME(22,0,0)), 'Open Insiden'!$A:$A, \"<\" & (A{r} + 1 + TIME(7,0,0))), B{r}=\"1.2\", COUNTIFS('Open Insiden'!$A:$A, \">=\" & (A{r} + TIME(6,0,0)), 'Open Insiden'!$A:$A, \"<\" & (A{r} + TIME(23,0,0))), B{r}=\"2.3\", COUNTIFS('Open Insiden'!$A:$A, \">=\" & (A{r} + TIME(14,0,0)), 'Open Insiden'!$A:$A, \"<\" & (A{r} + 1 + TIME(7,0,0))), TRUE, 0), \"-\")"
# E47
fE = f"=IFERROR(IFS(OR(B{r}=\"OFF\", LEFT(B{r},2)=\"IS\", B{r}=\"\"), \"-\", B{r}=\"1\", COUNTIFS('Closed Insiden'!$A:$A, \">=\" & (A{r} + TIME(6,0,0)), 'Closed Insiden'!$A:$A, \"<\" & (A{r} + TIME(15,0,0))), B{r}=\"2\", COUNTIFS('Closed Insiden'!$A:$A, \">=\" & (A{r} + TIME(14,0,0)), 'Closed Insiden'!$A:$A, \"<\" & (A{r} + TIME(23,0,0))), B{r}=\"3\", COUNTIFS('Closed Insiden'!$A:$A, \">=\" & (A{r} + TIME(22,0,0)), 'Closed Insiden'!$A:$A, \"<\" & (A{r} + 1 + TIME(7,0,0))), B{r}=\"1.2\", COUNTIFS('Closed Insiden'!$A:$A, \">=\" & (A{r} + TIME(6,0,0)), 'Closed Insiden'!$A:$A, \"<\" & (A{r} + TIME(23,0,0))), B{r}=\"2.3\", COUNTIFS('Closed Insiden'!$A:$A, \">=\" & (A{r} + TIME(14,0,0)), 'Closed Insiden'!$A:$A, \"<\" & (A{r} + 1 + TIME(7,0,0))), TRUE, 0), \"-\")"
# F47
fF = f"=IFERROR(IFS(B{r}=\"OFF\", \"OFF\", LEFT(B{r},2)=\"IS\", \"Izin Sakit\", B{r}=\"1\", \"Shift 1\", B{r}=\"2\", \"Shift 2\", B{r}=\"3\", \"Shift 3\", B{r}=\"1.2\", \"Shift 1 & 2\", B{r}=\"2.3\", \"Shift 2 & 3\", TRUE, B{r}), \"-\")"

updates = [
    ('A47', fA),
    ('C47', fC),
    ('D47', fD),
    ('E47', fE),
    ('F47', fF),
    ('B6', '=COUNTIFS(B11:B47, "<>OFF", B11:B47, "<>IS*", B11:B47, "<>-", B11:B47, "<>")'),
    ('C6', '=COUNTIF(B11:B47, "OFF")'),
    ('D6', '=SUM(D11:D47)'),
    ('E6', '=SUM(E11:E47)')
]

for rng, val in updates:
    res = kirim_perintah({
        'action': 'update',
        'tab_name': 'Summary',
        'range': rng,
        'value': val
    })
    print(f"Update {rng}: {res.get('status')}")
