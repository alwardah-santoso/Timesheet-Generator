import sys
import os
import concurrent.futures

sys.path.insert(0, '/home/homelinux/mini-project/running/timesheet-cleaner-spreadsheet-dev')
from sheets_adapter import kirim_perintah

def update_cell(r, c_let, val):
    payload = {
        "action": "update",
        "tab_name": "summary",
        "range": f"{c_let}{r}",
        "value": val
    }
    kirim_perintah(payload)

def get_cond(r, sheetName, startH, endH, addDay):
    start = f"(A{r} + TIME({startH};0;0))"
    end = f"(A{r} + {'1 + ' if addDay else ''}TIME({endH};0;0))"
    return f"SUMPRODUCT(('{sheetName}'!$C:$C=$C$4) * (IFERROR(VALUE('{sheetName}'!$A:$A); 0) >= {start}) * (IFERROR(VALUE('{sheetName}'!$A:$A); 0) < {end}))"

col_letters = ["B","C","D","E","F","G","H","I","J","K",
               "L","M","N","O","P","Q","R","S","T","U",
               "V","W","X","Y","Z","AA","AB","AC","AD",
               "AE","AF","AG","AH","AI","AJ","AK","AL"]

tasks = []

# KPI Formulas (B6:E6)
tasks.append((6, "B", '=COUNTIFS(B11:B47; "<>OFF"; B11:B47; "<>IS*"; B11:B47; "<>-"; B11:B47; "<>")'))
tasks.append((6, "C", '=COUNTIF(B11:B47; "OFF")'))
tasks.append((6, "D", '=SUM(D11:D47)'))
tasks.append((6, "E", '=SUM(E11:E47)'))

# Body Formulas (A11:F47)
for r in range(11, 48):
    cLet = col_letters[r - 11]
    # Reverted back to 7 (July) based on user feedback
    fA = f"=IF('Jadwal Shifting'!{cLet}$1=\"\"; \"\"; DATE(2026; 7; 'Jadwal Shifting'!{cLet}$1))"
    fB = f"=IF(OR(A{r}=\"\"; $C$4=\"\"); \"\"; IFERROR(INDEX('Jadwal Shifting'!$B$2:$AF$50; MATCH($C$4; 'Jadwal Shifting'!$A$2:$A$50; 0); MATCH(DAY(A{r}); 'Jadwal Shifting'!$B$1:$AF$1; 0)) & \"\"; \"-\"))"
    
    fC = f"""=IFERROR(IFS(B{r}="1"; "06:00 — 15:00"; B{r}="2"; "14:00 — 23:00"; B{r}="3"; "22:00 — 07:00"; B{r}="1.2"; "06:00 — 23:00"; B{r}="2.3"; "14:00 — 07:00"; TRUE; "-"); "-")"""
    
    fD = f"""=IFERROR(IFS(OR(B{r}="OFF"; LEFT(B{r};2)="IS"; B{r}=""); "-"; B{r}="1"; {get_cond(r, 'Open Insiden', 6, 15, False)}; B{r}="2"; {get_cond(r, 'Open Insiden', 14, 23, False)}; B{r}="3"; {get_cond(r, 'Open Insiden', 22, 7, True)}; B{r}="1.2"; {get_cond(r, 'Open Insiden', 6, 23, False)}; B{r}="2.3"; {get_cond(r, 'Open Insiden', 14, 7, True)}; TRUE; 0); "-")"""

    fE = f"""=IFERROR(IFS(OR(B{r}="OFF"; LEFT(B{r};2)="IS"; B{r}=""); "-"; B{r}="1"; {get_cond(r, 'Closed Insiden', 6, 15, False)}; B{r}="2"; {get_cond(r, 'Closed Insiden', 14, 23, False)}; B{r}="3"; {get_cond(r, 'Closed Insiden', 22, 7, True)}; B{r}="1.2"; {get_cond(r, 'Closed Insiden', 6, 23, False)}; B{r}="2.3"; {get_cond(r, 'Closed Insiden', 14, 7, True)}; TRUE; 0); "-")"""

    fF = f"""=IFERROR(IFS(B{r}="OFF"; "OFF"; LEFT(B{r};2)="IS"; "Izin Sakit"; B{r}="1"; "Shift 1"; B{r}="2"; "Shift 2"; B{r}="3"; "Shift 3"; B{r}="1.2"; "Shift 1 & 2"; B{r}="2.3"; "Shift 2 & 3"; TRUE; B{r}); "-")"""

    tasks.append((r, "A", fA))
    tasks.append((r, "B", fB))
    tasks.append((r, "C", fC))
    tasks.append((r, "D", fD))
    tasks.append((r, "E", fE))
    tasks.append((r, "F", fF))

print(f"Injecting {len(tasks)} formulas via concurrent API calls...")
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(update_cell, r, c, val) for r, c, val in tasks]
    concurrent.futures.wait(futures)

print("Done injecting formulas!")
