"""
fix_open_closed_formulas.py
---------------------------
Fix rumus E11:F41 (Open & Closed tiket) di sheet 'summary'.

Masalah sebelumnya:
  - Rumus merujuk A{r} sebagai tanggal, padahal kolom A sengaja dikosongkan.
  - Referensi shift juga ikut kolom B (asumsi lama A=tanggal, B=shift).

Fix:
  - Tanggal  : A{r} → B{r}  (kolom B = tanggal aktual)
  - Shift    : B{r} → C{r}  (kolom C = shift aktual)
  - Semua kolom lain tidak diubah.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import kirim_perintah

SEP = ";"   # separator Google Sheets (locale Indonesia)
TAB = "summary"


def get_cond(r, sheet_name, start_h, end_h, add_day):
    """
    SUMPRODUCT untuk menghitung insiden dalam jendela waktu shift.
      - Tanggal referensi : B{r}
      - Nama petugas      : kolom C di sheet insiden vs $C$4 (nama konsultan)
      - Datetime insiden  : kolom A di sheet insiden
    """
    start = f"(B{r} + TIME({start_h}{SEP}0{SEP}0))"
    end   = f"(B{r}{' + 1' if add_day else ''} + TIME({end_h}{SEP}0{SEP}0))"
    return (
        f"SUMPRODUCT(('{sheet_name}'!$C:$C=$C$4) * "
        f"(IFERROR(VALUE('{sheet_name}'!$A:$A){SEP} 0) >= {start}) * "
        f"(IFERROR(VALUE('{sheet_name}'!$A:$A){SEP} 0) < {end}))"
    )


def build_open_formula(r):
    """Rumus kolom E (Open Insiden) untuk baris r."""
    return (
        f'=IFERROR(IFS('
        f'OR(C{r}="OFF"{SEP} LEFT(C{r}{SEP}2)="IS"{SEP} C{r}=""){SEP} "-"{SEP} '
        f'C{r}="1"{SEP} {get_cond(r, "Open Insiden", 6, 15, False)}{SEP} '
        f'C{r}="2"{SEP} {get_cond(r, "Open Insiden", 14, 23, False)}{SEP} '
        f'C{r}="3"{SEP} {get_cond(r, "Open Insiden", 22, 7, True)}{SEP} '
        f'C{r}="1.2"{SEP} {get_cond(r, "Open Insiden", 6, 23, False)}{SEP} '
        f'C{r}="2.3"{SEP} {get_cond(r, "Open Insiden", 14, 7, True)}{SEP} '
        f'TRUE{SEP} 0){SEP} "-")'
    )


def build_closed_formula(r):
    """Rumus kolom F (Closed Insiden) untuk baris r."""
    return (
        f'=IFERROR(IFS('
        f'OR(C{r}="OFF"{SEP} LEFT(C{r}{SEP}2)="IS"{SEP} C{r}=""){SEP} "-"{SEP} '
        f'C{r}="1"{SEP} {get_cond(r, "Closed Insiden", 6, 15, False)}{SEP} '
        f'C{r}="2"{SEP} {get_cond(r, "Closed Insiden", 14, 23, False)}{SEP} '
        f'C{r}="3"{SEP} {get_cond(r, "Closed Insiden", 22, 7, True)}{SEP} '
        f'C{r}="1.2"{SEP} {get_cond(r, "Closed Insiden", 6, 23, False)}{SEP} '
        f'C{r}="2.3"{SEP} {get_cond(r, "Closed Insiden", 14, 7, True)}{SEP} '
        f'TRUE{SEP} 0){SEP} "-")'
    )


def main():
    # Build 2D array [[E11,F11], [E12,F12], ..., [E41,F41]]
    values = []
    for r in range(11, 42):
        values.append([build_open_formula(r), build_closed_formula(r)])

    print(f"Mengupdate E11:F41 ({len(values)} baris) di tab '{TAB}'...")
    print(f"Contoh E11: {values[0][0][:120]}...")
    print(f"Contoh F11: {values[0][1][:120]}...")
    print()

    res = kirim_perintah({
        'action': 'update',
        'tab_name': TAB,
        'range': 'E11:F41',
        'values': values
    })

    status = res.get('status', 'unknown')
    print(f"Hasil: {status}")
    if status != 'success':
        print(f"Detail: {res}")


if __name__ == '__main__':
    main()
