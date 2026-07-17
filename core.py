"""
core.py
-------
Shared processing logic untuk Timesheet Cleaner.
Di-import oleh server.py (web) dan process_data.py (CLI) untuk memastikan
konsistensi output JSON di kedua mode penggunaan.

Fix yang ada di sini:
- ISSUE-01: Deteksi num_days secara dinamis (tidak hardcode 1:32)
- ISSUE-02: Deteksi bulan/tahun dari mode(), bukan hanya baris pertama
- ISSUE-05: prepared_date menggunakan calendar.monthrange (bukan days_data[-1])
- BUG-03:   Output selalu punya field 'summary' dan 'notes'
- MINOR-10: normalize_incident_title() dipanggil di kedua sheet
"""

import pandas as pd
import re
import calendar
from datetime import datetime, timedelta
from config import settings

# ============================================================
# NORMALISASI NAMA INSIDEN
# ============================================================
NORMALIZATION_MAP = settings.normalization_map


def normalize_name(name):
    """Normalisasi nama insiden: exact match map + kode alphanumerik."""
    name = str(name).strip()
    if name.upper() in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[name.upper()]
    # Kode alphanumerik (misal 26J41246, ABC-12345) → REQUEST RANGING
    if re.match(r'^[A-Z0-9]{4,}$', name) and re.search(r'[0-9]', name) and re.search(r'[A-Z]', name):
        return 'REQUEST RANGING'
    return name


def normalize_incident_title(title):
    """Auto-correct typo dan normalisasi judul insiden (dijalankan sebelum normalize_name)."""
    if not isinstance(title, str):
        return title
    t = title.strip().upper()
    TYPO_MAP = settings.typo_map
    if t in TYPO_MAP:
        return TYPO_MAP[t]
    # REAKTIVASI SIMCARD normalization (case-insensitive)
    if 'REAKTIVASI' in t:
        return 'REAKTIVASI SIMCARD'
    # Pola kode tiket (misal: ABC-123, 26J41246) → REQUEST RANGING
    if re.match(r'^[0-9A-Z]+-[0-9A-Z]*$', t) or re.match(r'^[0-9]{2,}[A-Z][0-9]+$', t):
        return 'REQUEST RANGING'
    return title.strip()


# ============================================================
# PARSE TANGGAL CLOSED INSIDEN
# ============================================================
def parse_closed_datetime(v):
    """Parse ClosedDateTime. Excel datetime → langsung pakai. String → parse."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return pd.NaT
    # Excel datetime objects already correct — DON'T swap month/day
    if hasattr(v, 'year') and hasattr(v, 'month') and hasattr(v, 'day'):
        try:
            if pd.isna(pd.Timestamp(v)):
                return pd.NaT
            return v
        except Exception:
            return pd.NaT
    # String format: parse with dayfirst
    return pd.to_datetime(v, dayfirst=True, errors='coerce')


# ============================================================
# FILTER INSIDEN BERDASARKAN RENTANG WAKTU
# ============================================================
def get_incidents(df, start_dt, end_dt):
    mask = (df['datetime'] >= start_dt) & (df['datetime'] < end_dt)
    counts = df[mask]['nama'].value_counts().to_dict()
    return {k: int(v) for k, v in counts.items()}


# ============================================================
# BUILD DATA PER HARI
# ============================================================
def _build_timesheet_result(found_name: str, year: int, month: int, days_data: list, notes_list: list, tasks: list = None) -> dict:
    """Helper terpusat untuk membangun dictionary output ringkasan bulanan (REF-01)."""
    summary = []
    for d in days_data:
        if d['type'] not in ['OFF', 'IS']:
            if d['type'] == 'S12':
                o = sum(d['open_s1'].values()) + sum(d['open_s2'].values())
                c = sum(d['closed_s1'].values()) + sum(d['closed_s2'].values())
            elif d['type'] == 'S23':
                o = sum(d['open_s2'].values()) + sum(d['open_s3'].values())
                c = sum(d['closed_s2'].values()) + sum(d['closed_s3'].values())
            else:
                o = sum(d['open'].values())
                c = sum(d['closed'].values())
            summary.append({'day': d['day'], 'type': d['type'], 'open': o, 'closed': c})

    month_names_id = settings.month_names_id
    last_day = calendar.monthrange(year, month)[1]

    if tasks is None:
        tasks = []
        for val in notes_list:
            val_clean = str(val).strip()
            if val_clean and val_clean.lower() != 'nan':
                val_clean = val_clean.lstrip('- ').strip()
                tasks.append(val_clean)

    output = {
        'employee_name': found_name,
        'consultant_role': 'Operator',
        'month': month,
        'year': year,
        'month_label': f"{month_names_id[month - 1]} {year}",
        'prepared_date': f"{last_day} {month_names_id[month - 1]} {year}",
        'tasks': tasks,
        'days': days_data,
        'summary': summary,
        'notes': notes_list,
    }
    return output


def build_day_data(shifts, df_open, df_closed, year, month, backup_info=None, cell_colors=None):
    """Membangun data per hari berdasarkan shifts dan data insiden (Configuration-Driven REF-02)."""
    days = []
    shift_defs = settings.shift_definitions
    for day_idx, shift in enumerate(shifts):
        day = day_idx + 1
        shift_str = str(shift).strip()
        d = datetime(year, month, day)
        date_str = d.strftime('%d/%m/%Y')
        color_key = cell_colors[day_idx] if cell_colors and day_idx < len(cell_colors) else 'white'

        if shift_str in ['OFF', 'nan', '']:
            days.append({'day': day, 'date': date_str, 'type': 'OFF', 'shift': shift_str, 'color': color_key})
        elif shift_str.upper().startswith('IS'):
            days.append({'day': day, 'date': date_str, 'type': 'IS', 'shift': shift_str, 'color': color_key})
        elif shift_str in shift_defs:
            sdef = shift_defs[shift_str]
            stype = sdef['type']

            # Helper untuk ambil backup_name
            backup_name = '(Tidak Diketahui)'
            if backup_info and stype in ['S12', 'S23']:
                for info in backup_info:
                    if info.get('day') == day:
                        backup_name = info.get('name', '(Tidak Diketahui)')
                        break

            if shift_str in ['1', '2']:
                start_hr = int(sdef['start'].split(':')[0])
                end_hr = int(sdef['end'].split(':')[0])
                start, end = d.replace(hour=start_hr), d.replace(hour=end_hr)
                o = get_incidents(df_open, start, end)
                c = get_incidents(df_closed, start, end)
                days.append({'day': day, 'date': date_str, 'type': stype, 'shift': shift_str, 'color': color_key,
                             'start': sdef['start'], 'end': sdef['end'], 'remark': sdef['remark'], 'open': o, 'closed': c})
            elif shift_str == '3':
                start = d.replace(hour=22)
                end = (d + timedelta(days=1)).replace(hour=7)
                o = get_incidents(df_open, start, end)
                c = get_incidents(df_closed, start, end)
                days.append({'day': day, 'date': date_str, 'type': stype, 'shift': shift_str, 'color': color_key,
                             'start': sdef['start'], 'end': sdef['end'], 'remark': sdef['remark'], 'open': o, 'closed': c})
            elif shift_str == '1.2':
                s1_start, s1_end = d.replace(hour=6), d.replace(hour=14)
                s2_start, s2_end = d.replace(hour=14), d.replace(hour=23)
                o1 = get_incidents(df_open, s1_start, s1_end)
                c1 = get_incidents(df_closed, s1_start, s1_end)
                o2 = get_incidents(df_open, s2_start, s2_end)
                c2 = get_incidents(df_closed, s2_start, s2_end)
                days.append({'day': day, 'date': date_str, 'type': stype, 'shift': shift_str, 'color': color_key,
                             'start': sdef['start'], 'end': sdef['end'], 'remark': sdef['remark'],
                             'backup_name': backup_name,
                             'open_s1': o1, 'closed_s1': c1, 'open_s2': o2, 'closed_s2': c2})
            elif shift_str == '2.3':
                s2_start, s2_end = d.replace(hour=14), d.replace(hour=22)
                s3_start = d.replace(hour=22)
                s3_end = (d + timedelta(days=1)).replace(hour=7)
                o2 = get_incidents(df_open, s2_start, s2_end)
                c2 = get_incidents(df_closed, s2_start, s2_end)
                o3 = get_incidents(df_open, s3_start, s3_end)
                c3 = get_incidents(df_closed, s3_start, s3_end)
                days.append({'day': day, 'date': date_str, 'type': stype, 'shift': shift_str, 'color': color_key,
                             'start': sdef['start'], 'end': sdef['end'], 'remark': sdef['remark'],
                             'backup_name': backup_name,
                             'open_s2': o2, 'closed_s2': c2, 'open_s3': o3, 'closed_s3': c3})
        else:
            print(f"  [WARNING] Hari {day}: shift '{shift_str}' tidak dikenali, diperlakukan sebagai OFF")
            days.append({'day': day, 'date': date_str, 'type': 'OFF', 'shift': shift_str, 'color': color_key})

    return days


# ============================================================
# HELPER: PARSE INCIDENT SHEET
# ============================================================
def parse_incident_sheet(df_raw, max_cols=2):
    """Parse a 2-column incident sheet, detecting headers and column order."""
    df = df_raw.iloc[:, :max_cols].copy()

    row0 = [str(v).strip() for v in df.iloc[0].tolist()]
    is_header = any(
        kw in row0_val.lower()
        for row0_val in row0
        for kw in ['nama', 'insiden', 'incident', 'time', 'date', 'detected', 'closed', 'petugas']
    )

    if is_header:
        df = df.iloc[1:].reset_index(drop=True)

    df.columns = ['col0', 'col1']

    if len(df) > 0:
        sample0 = df['col0'].iloc[0]
        sample1 = df['col1'].iloc[0]
        col0_is_dt = hasattr(sample0, 'year') or (
            isinstance(sample0, str) and re.search(r'\d{4}', str(sample0))
        )
        col1_is_dt = hasattr(sample1, 'year') or (
            isinstance(sample1, str) and re.search(r'\d{4}', str(sample1))
        )
        if col0_is_dt and not col1_is_dt:
            df.columns = ['datetime', 'nama']
        elif col1_is_dt and not col0_is_dt:
            df.columns = ['nama', 'datetime']
        else:
            df.columns = ['datetime', 'nama']
    else:
        df.columns = ['datetime', 'nama']

    return df


# ============================================================
# MAIN PROCESSING FUNCTION
# ============================================================
def process_excel(excel_path: str, target_name: str = None):
    """
    Core processing logic. Returns (names_list, output_dict or None).

    Fixes vs original:
    - num_days dideteksi dinamis dari header (ISSUE-01)
    - Bulan/tahun dari mode() seluruh data, bukan hanya baris pertama (ISSUE-02)
    - prepared_date pakai calendar.monthrange (ISSUE-05)
    - normalize_incident_title() dipanggil di kedua sheet (MINOR-10)
    - Output selalu punya field 'summary' dan 'notes' (BUG-03)
    """
    xl = pd.ExcelFile(excel_path)

    # ── Jadwal Shifting ──────────────────────────────────────
    df_sched = pd.read_excel(xl, sheet_name='Jadwal Shifting', header=None)
    all_names = []
    for row_idx in range(2, len(df_sched)):
        name = str(df_sched.iloc[row_idx, 0]).strip()
        if name and name.lower() != 'nan':
            if re.search(r'backup|izin sakit|tanggal\s+\d+', name, re.IGNORECASE):
                continue
            all_names.append((row_idx, name))

    names_list = [n for _, n in all_names]

    if not target_name:
        return names_list, None

    # Cari target
    target_row = None
    found_name = None
    for row_idx, name in all_names:
        if name.lower() == target_name.lower():
            target_row = row_idx
            found_name = name
            break

    if target_row is None:
        raise ValueError(f"Nama '{target_name}' tidak ditemukan.")

    # ── ISSUE-01 FIX: Deteksi num_days secara dinamis ────────
    num_days = 0
    for col_idx in range(1, len(df_sched.columns)):
        val = df_sched.iloc[0, col_idx]
        try:
            int(val)
            num_days += 1
        except (ValueError, TypeError):
            break
    shifts = df_sched.iloc[target_row, 1:num_days + 1].tolist()

    # ── Baca warna sel via openpyxl ──────────────────────────
    cell_colors = []
    try:
        import openpyxl as opx
        wb = opx.load_workbook(excel_path)
        ws = wb['Jadwal Shifting']
        for col_idx in range(2, num_days + 2):
            cell = ws.cell(row=target_row + 1, column=col_idx)
            fill = cell.fill
            fg = fill.fgColor
            if fg.type == 'rgb' and fg.rgb and fg.rgb != '00000000':
                rgb = str(fg.rgb)
                if rgb == 'FFFFFF00':
                    cell_colors.append('yellow')
                elif rgb == 'FF00FF00':
                    cell_colors.append('green')
                elif rgb == 'FFFFFFFF':
                    cell_colors.append('white')
                elif rgb == 'FF1010EA':
                    cell_colors.append('blue')
                else:
                    cell_colors.append('white')
            elif fg.type == 'theme':
                cell_colors.append('brown')
            else:
                cell_colors.append('white')
        wb.close()
        print(f"  Cell colors: {len(cell_colors)} detected")
    except Exception as e:
        print(f"  Warning: could not read colors: {e}")
        cell_colors = ['white'] * num_days

    # ── Backup info ──────────────────────────────────────────
    backup_info = []
    if 'Backup' in xl.sheet_names:
        df_backup = pd.read_excel(xl, sheet_name='Backup', header=None)
        for row_idx in range(1, len(df_backup)):
            try:
                day_val = int(df_backup.iloc[row_idx, 0])
                col1_val = str(df_backup.iloc[row_idx, 1]).strip() if df_backup.shape[1] > 1 else ''
                col2_val = str(df_backup.iloc[row_idx, 2]).strip() if df_backup.shape[1] > 2 else ''
                shift_val = str(df_backup.iloc[row_idx, 3]).strip() if df_backup.shape[1] > 3 else ''

                # Jika format 3/4 kolom (Karyawan Utama & Nama Backup tersedia)
                if col2_val and col2_val.lower() != 'nan':
                    emp_name = col1_val
                    backup_name = col2_val
                    if emp_name and emp_name.lower() != 'nan' and emp_name.lower() == target_name.lower():
                        backup_info.append({'day': day_val, 'name': backup_name, 'shift': shift_val})
                # Jika format sederhana 2 kolom (Tanggal | Nama Karyawan/Backup)
                elif col1_val and col1_val.lower() != 'nan':
                    backup_info.append({'day': day_val, 'name': col1_val, 'shift': shift_val})
            except (ValueError, TypeError, IndexError):
                continue
        print(f"  Backup sheet: {len(backup_info)} entries loaded")
    else:
        # Fallback: parse dari Jadwal Shifting notes (legacy)
        if len(df_sched) > 4:
            for extra_row in range(4, len(df_sched)):
                note = str(df_sched.iloc[extra_row, 0]).strip()
                if 'backup' in note.lower() or 'izin sakit' in note.lower():
                    day_match = re.search(r'tanggal\s+(\d+)', note, re.IGNORECASE)
                    name_match = re.search(r'izin sakit\s+(.+?)(?:\s+shift|\s*$)', note, re.IGNORECASE)
                    if not name_match:
                        name_match = re.search(r'backup\s+(.+?)(?:\s+shift|\s*izin|\s*$)', note, re.IGNORECASE)
                    if day_match and name_match:
                        backup_info.append({'day': int(day_match.group(1)), 'name': name_match.group(1).strip()})
        print(f"  Backup from notes (legacy): {len(backup_info)} entries")

    # ── Notes ─────────────────────────────────────────────────
    notes_list = []
    if 'Notes' in xl.sheet_names:
        df_notes_sheet = pd.read_excel(xl, sheet_name='Notes', header=None)
        for row_idx in range(len(df_notes_sheet)):
            val = str(df_notes_sheet.iloc[row_idx, 0]).strip()
            if val and val.lower() != 'nan':
                notes_list.append(val)
        print(f"  Notes: {len(notes_list)} entries loaded")

    # ── Open Insiden ─────────────────────────────────────────
    df_open_raw = pd.read_excel(xl, sheet_name='Open Insiden', header=None)
    if df_open_raw.shape[1] >= 3:
        first_row = [str(v).strip().lower() for v in df_open_raw.iloc[0].tolist()]
        if 'nama petugas' in first_row:
            df_open_raw.columns = df_open_raw.iloc[0]
            df_open_raw = df_open_raw.iloc[1:].reset_index(drop=True)
            petugas_col = next(c for c in df_open_raw.columns if str(c).lower() == 'nama petugas')
            dt_col = next((c for c in df_open_raw.columns if 'time' in str(c).lower() or 'detected' in str(c).lower()), df_open_raw.columns[1])
            insiden_col = next((c for c in df_open_raw.columns if 'insiden' in str(c).lower() or 'incident' in str(c).lower()), df_open_raw.columns[0])
            df_open = df_open_raw[[dt_col, insiden_col, petugas_col]].copy()
            df_open.columns = ['datetime', 'nama', 'petugas']
            df_open = df_open[df_open['petugas'].str.strip().str.lower() == found_name.lower()].copy()
        else:
            df_open = parse_incident_sheet(df_open_raw)
    else:
        df_open = parse_incident_sheet(df_open_raw)

    df_open['datetime'] = pd.to_datetime(df_open['datetime'], errors='coerce')
    df_open = df_open.dropna(subset=['datetime'])
    # MINOR-10 FIX: normalize_incident_title dijalankan juga di CLI mode
    df_open['nama'] = df_open['nama'].apply(normalize_incident_title)
    df_open['nama'] = df_open['nama'].apply(normalize_name)

    # ── Closed Insiden ───────────────────────────────────────
    df_closed_raw = pd.read_excel(xl, sheet_name='Closed Insiden', header=None)
    if df_closed_raw.shape[1] >= 3:
        first_row = [str(v).strip().lower() for v in df_closed_raw.iloc[0].tolist()]
        if 'nama petugas' in first_row:
            df_closed_raw.columns = df_closed_raw.iloc[0]
            df_closed_raw = df_closed_raw.iloc[1:].reset_index(drop=True)
            petugas_col = next(c for c in df_closed_raw.columns if str(c).lower() == 'nama petugas')
            dt_col = df_closed_raw.columns[0]
            insiden_col = next((c for c in df_closed_raw.columns if 'insiden' in str(c).lower() or 'incident' in str(c).lower()), df_closed_raw.columns[1])
            df_closed = df_closed_raw[[dt_col, insiden_col, petugas_col]].copy()
            df_closed.columns = ['datetime', 'nama', 'petugas']
            df_closed = df_closed[df_closed['petugas'].str.strip().str.lower() == found_name.lower()].copy()
        else:
            df_closed = parse_incident_sheet(df_closed_raw)
    else:
        df_closed = parse_incident_sheet(df_closed_raw)

    df_closed['datetime'] = df_closed['datetime'].apply(parse_closed_datetime)
    df_closed = df_closed.dropna(subset=['datetime'])
    # MINOR-10 FIX: normalize_incident_title dijalankan juga di CLI mode
    df_closed['nama'] = df_closed['nama'].apply(normalize_incident_title)
    df_closed['nama'] = df_closed['nama'].apply(normalize_name)

    # ── ISSUE-02 FIX: Deteksi bulan/tahun dari mode(), bukan baris pertama ──
    if len(df_open) > 0:
        month = int(df_open['datetime'].dt.month.mode()[0])
        year  = int(df_open['datetime'].dt.year.mode()[0])
    elif len(df_closed) > 0:
        month = int(df_closed['datetime'].dt.month.mode()[0])
        year  = int(df_closed['datetime'].dt.year.mode()[0])
    else:
        raise ValueError("Tidak ada data insiden ditemukan.")

    # ── Tasks dari Notes ──────────────────────────────────────
    tasks = []
    if 'Notes' in xl.sheet_names:
        df_notes = pd.read_excel(xl, sheet_name='Notes', header=None)
        for _, row in df_notes.iterrows():
            val = str(row[0]).strip()
            if val and val.lower() != 'nan':
                val = val.lstrip('- ').strip()
                tasks.append(val)

    # ── Build day data ────────────────────────────────────────
    days_data = build_day_data(shifts, df_open, df_closed, year, month, backup_info, cell_colors)

    output = _build_timesheet_result(found_name, year, month, days_data, notes_list, tasks=tasks)
    return names_list, output


# ============================================================
# PROCESS FROM GOOGLE SHEETS DATA
# ============================================================
def process_from_sheets_data(sheets_data: dict, target_name: str = None):
    """
    Process timesheet data from Google Sheets (via sheets_adapter).
    Same output as process_excel() but takes pre-built data instead of Excel path.

    Args:
        sheets_data: dict from sheets_adapter.build_dataframes() containing:
            - 'shifts': list of shift values
            - 'found_name': matched employee name
            - 'num_days': number of days
            - 'df_open': DataFrame with 'datetime' and 'nama' columns
            - 'df_closed': DataFrame with 'datetime' and 'nama' columns
            - 'backup_info': list of backup dicts
            - 'notes_list': list of note strings
            - 'names_list': list of all employee names
        target_name: if None, return (names_list, None)

    Returns:
        Same format as process_excel(): (names_list, output_dict or None)
    """
    names_list = sheets_data['names_list']

    # Jika target_name tidak diberikan, kembalikan daftar nama saja
    if target_name is None:
        return names_list, None

    # ── Ambil data dari sheets_data ──────────────────────────
    shifts = sheets_data['shifts']
    found_name = sheets_data['found_name']
    num_days = sheets_data['num_days']
    df_open = sheets_data['df_open'].copy()
    df_closed = sheets_data['df_closed'].copy()
    backup_info = sheets_data.get('backup_info', [])
    notes_list = sheets_data.get('notes_list', [])

    # ── Cell colors: default putih karena Google Sheets tidak punya warna sel ──
    if 'cell_colors' in sheets_data:
        cell_colors = sheets_data['cell_colors']
    else:
        cell_colors = ['white'] * num_days

    # ── MINOR-10 FIX: normalize_incident_title + normalize_name pada kedua sheet ──
    df_open['nama'] = df_open['nama'].apply(normalize_incident_title)
    df_open['nama'] = df_open['nama'].apply(normalize_name)
    df_closed['nama'] = df_closed['nama'].apply(normalize_incident_title)
    df_closed['nama'] = df_closed['nama'].apply(normalize_name)

    # ── ISSUE-02 FIX: Deteksi bulan/tahun dari mode(), bukan baris pertama ──
    if len(df_open) > 0:
        month = int(df_open['datetime'].dt.month.mode()[0])
        year  = int(df_open['datetime'].dt.year.mode()[0])
    elif len(df_closed) > 0:
        month = int(df_closed['datetime'].dt.month.mode()[0])
        year  = int(df_closed['datetime'].dt.year.mode()[0])
    else:
        raise ValueError("Tidak ada data insiden ditemukan.")

    # ── Build day data ────────────────────────────────────────
    days_data = build_day_data(shifts, df_open, df_closed, year, month, backup_info, cell_colors)

    output = _build_timesheet_result(found_name, year, month, days_data, notes_list, tasks=None)
    return names_list, output
