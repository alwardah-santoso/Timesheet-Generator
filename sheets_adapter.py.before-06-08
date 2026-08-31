"""
sheets_adapter.py
-----------------
Adapter module to read timesheet data from Google Sheets via Apps Script Web App.
Provides functions to fetch and parse each tab, then build DataFrames for
core.process_from_sheets_data().

No Google Cloud / Service Account needed — uses existing Apps Script URL.
"""

import sys
import os
import urllib.request
import urllib.parse
import json
import re
import pandas as pd

# ── Ensure project directory is on sys.path for imports ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings

# ── Constants ──────────────────────────────────────────────────────────────
WEB_APP_URL = settings.web_app_url
TIMESHEET_SS_ID = settings.timesheet_ss_id


# ── Core read/write helpers (self-contained, no import from panggil_gss) ──

def _resolve_ss_id(ss_id=None):
    """Resolve spreadsheet ID, falling back to settings if not provided."""
    target = ss_id if (ss_id is not None and str(ss_id).strip() != "") else settings.timesheet_ss_id
    if not target or str(target).strip() == "":
        raise ValueError("ID Google Spreadsheet belum dikonfigurasi. Harap buat/isi file .env dengan TIMESHEET_SS_ID=<ID_SPREADSHEET> atau masukkan via antarmuka Web UI.")
    return str(target).strip()


def kirim_perintah(payload_dict):
    """Send a POST command to the Google Apps Script Web App."""
    payload_dict = dict(payload_dict)
    if not payload_dict.get("id"):
        payload_dict["id"] = _resolve_ss_id(None)
    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(
        WEB_APP_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"status": "error", "message": str(e)}


def baca_data(ss_id=None, tab_name=None):
    """Read all rows from a spreadsheet tab via the Apps Script Web App."""
    target_ss_id = _resolve_ss_id(ss_id)
    url = f"{WEB_APP_URL}?id={target_ss_id}"
    if tab_name:
        url += f"&tab={urllib.parse.quote(tab_name)}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [sheets_adapter] Error reading tab '{tab_name}': {e}")
        return []


# ── Name matching helpers ──────────────────────────────────────────────────

def normalize_emp_token_str(name):
    if not name or pd.isna(name):
        return ""
    n = str(name).strip().lower()
    n = n.replace(".", " ").replace(",", " ")
    n = re.sub(r"\bmuhammad\b|\bmuhamad\b", "m", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

def match_employee_name(name1, name2):
    if not name1 or not name2:
        return False
    n1 = normalize_emp_token_str(name1)
    n2 = normalize_emp_token_str(name2)
    if n1 == n2:
        return True
    toks1 = n1.split()
    toks2 = n2.split()
    if len(toks1) >= 2 and len(toks1) <= len(toks2):
        if all(t in toks2 for t in toks1):
            return True
    if len(toks2) >= 2 and len(toks2) <= len(toks1):
        if all(t in toks1 for t in toks2):
            return True
    if len(toks1) == 1 and len(toks2) >= 1 and toks1[0] == toks2[0]:
        return True
    if len(toks2) == 1 and len(toks1) >= 1 and toks2[0] == toks1[0]:
        return True
    return False


# ── Parse helpers ──────────────────────────────────────────────────────────


def _smart_parse_datetime_col(series):
    """Parse a Series of datetime strings that may contain mixed ISO8601 and DD/MM/YYYY formats.
    Vectorized: splits into ISO and non-ISO groups for correct dayfirst handling.
    Returns naive datetime64 Series (no timezone)."""
    series = series.astype(str)
    is_iso = series.str.contains('T', na=False)

    if is_iso.all():
        result = pd.to_datetime(series, errors='coerce')
    elif (~is_iso).all():
        result = pd.to_datetime(series, dayfirst=True, errors='coerce')
    else:
        # Mixed formats — parse each group separately and combine
        result_iso = pd.to_datetime(series[is_iso], errors='coerce')
        result_non = pd.to_datetime(series[~is_iso], dayfirst=True, errors='coerce')
        # Convert ISO (may have UTC tz) to naive for compatibility
        if hasattr(result_iso.dtype, 'tz') and result_iso.dtype.tz is not None:
            result_iso = result_iso.dt.tz_localize(None)
        # Combine into a single naive Series
        result = pd.Series(index=series.index, dtype='datetime64[us]')
        result.loc[is_iso] = result_iso.values
        result.loc[~is_iso] = result_non.values

    # Correct US locale month/day swapping (e.g. 01/06/2026 parsed as Jan 6th instead of June 1st)
    unambiguous = result[result.dt.day > 12]
    if len(unambiguous) > 0:
        target_month = int(unambiguous.dt.month.mode()[0])
        mask = (result.dt.day == target_month) & (result.dt.month != target_month)
        if mask.any():
            result = result.copy()
            for idx, val in result[mask].items():
                if pd.notna(val):
                    try:
                        result.loc[idx] = val.replace(month=val.day, day=val.month)
                    except ValueError:
                        pass
    return result


def _parse_incident_sheet_from_rows(rows):
    """
    Parse a 2-or-3 column incident sheet from raw row data (list of lists).
    Mirrors core.parse_incident_sheet logic but works on raw lists instead of
    a DataFrame.
    
    Returns a DataFrame with columns ['datetime', 'nama'].
    """
    if not rows:
        return pd.DataFrame(columns=['datetime', 'nama'])

    # Detect if first row is a header
    row0 = [str(v).strip() for v in rows[0]]
    is_header = any(
        kw in row0_val.lower()
        for row0_val in row0
        for kw in ['nama', 'insiden', 'incident', 'time', 'date', 'detected', 'closed', 'petugas']
    )

    data_rows = rows[1:] if is_header else rows

    # Take only first 2 columns (datetime, nama)
    data = []
    for row in data_rows:
        if len(row) >= 2:
            data.append([row[0], row[1]])
        elif len(row) == 1:
            data.append([row[0], None])
        # skip empty rows

    df = pd.DataFrame(data, columns=['col0', 'col1'])

    # Detect which column is datetime
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
            df = df[['datetime', 'nama']]
        else:
            df.columns = ['datetime', 'nama']
    else:
        df.columns = ['datetime', 'nama']

    df['datetime'] = _smart_parse_datetime_col(df['datetime'])
    # Remove timezone info if present (core.py uses naive datetimes)
    if hasattr(df['datetime'].dtype, 'tz') and df['datetime'].dtype.tz is not None:
        df['datetime'] = df['datetime'].dt.tz_localize(None)
    df['nama'] = df['nama'].apply(lambda x: str(x).strip() if x is not None else '')
    df = df.dropna(subset=['datetime'])

    return df


def _parse_incident_3col(rows, target_name):
    """
    Parse a 3-column incident sheet where columns are:
    [datetime, nama_insiden, nama_petugas].
    Filter rows where nama_petugas matches target_name.
    
    Returns a DataFrame with columns ['datetime', 'nama'].
    """
    if not rows:
        return pd.DataFrame(columns=['datetime', 'nama'])

    # First row should be header with 'nama petugas'
    row0 = [str(v).strip().lower() for v in rows[0]]
    if 'nama petugas' in row0:
        # Find column indices
        petugas_idx = next(i for i, v in enumerate(row0) if v == 'nama petugas')
        # The other two: datetime and nama insiden
        other_idxs = [i for i in range(len(row0)) if i != petugas_idx]
        # Determine which 'other' is datetime (has 'time'/'date'/'detected') vs insiden
        dt_idx = None
        insiden_idx = None
        for i in other_idxs:
            val = row0[i]
            if 'time' in val or 'date' in val or 'detected' in val or 'closed' in val:
                dt_idx = i
            elif 'insiden' in val or 'incident' in val or 'nama' in val:
                insiden_idx = i
        if dt_idx is None:
            dt_idx = other_idxs[0]
        if insiden_idx is None:
            insiden_idx = other_idxs[1] if len(other_idxs) > 1 else other_idxs[0]

        data_rows = rows[1:]
        records = []
        for row in data_rows:
            if len(row) <= petugas_idx:
                continue
            petugas_val = str(row[petugas_idx]).strip() if row[petugas_idx] is not None else ''
            if match_employee_name(petugas_val, target_name):
                dt_val = row[dt_idx] if dt_idx < len(row) else None
                ins_val = row[insiden_idx] if insiden_idx < len(row) else None
                records.append([dt_val, ins_val])

        df = pd.DataFrame(records, columns=['datetime', 'nama'])
        df['datetime'] = _smart_parse_datetime_col(df['datetime'])
        # Remove timezone info if present (core.py uses naive datetimes)
        if hasattr(df['datetime'].dtype, 'tz') and df['datetime'].dtype.tz is not None:
            df['datetime'] = df['datetime'].dt.tz_localize(None)
        df['nama'] = df['nama'].apply(lambda x: str(x).strip() if x is not None else '')
        df = df.dropna(subset=['datetime'])
        return df
    else:
        # Not a 3-col header with 'nama petugas' — fall back to 2-col parse
        return _parse_incident_sheet_from_rows(rows)


# ── Main builder ───────────────────────────────────────────────────────────

def build_dataframes(ss_id=None):
    """
    Read all tabs from the Google Sheets timesheet and build the data dict
    expected by core.process_from_sheets_data().
    
    Returns a dict with keys:
        'shifts', 'found_name', 'num_days', 'df_open', 'df_closed',
        'backup_info', 'notes_list', 'names_list', 'cell_colors',
        '_raw_sched' (internal cache for get_shifts_for_name)
    
    shifts and found_name are None at this stage — they get filled in
    when the server calls get_shifts_for_name() after the user selects a name.
    """
    target_ss_id = _resolve_ss_id(ss_id)
    # ── 1. Jadwal Shifting ──────────────────────────────────────────────
    raw_sched = baca_data(target_ss_id, tab_name="Jadwal Shifting")
    if not raw_sched or len(raw_sched) < 3:
        raise ValueError("Tab 'Jadwal Shifting' kosong atau tidak ditemukan di Google Sheets.")

    # Row 0: day numbers (1, 2, 3, ...)
    row0 = raw_sched[0]
    num_days = 0
    for col_idx in range(1, len(row0)):
        try:
            int(row0[col_idx])
            num_days += 1
        except (ValueError, TypeError):
            break

    if num_days == 0:
        raise ValueError("Tidak bisa mendeteksi jumlah hari dari tab 'Jadwal Shifting'.")

    # Row 1: "NAMA" header + day-of-week labels
    # Row 2+: employee names (col 0) + shift values (col 1+)
    names_list = []
    for row_idx in range(2, len(raw_sched)):
        name = str(raw_sched[row_idx][0]).strip() if raw_sched[row_idx] and raw_sched[row_idx][0] is not None else ''
        if name and name.lower() != 'nan':
            # Skip backup / izin sakit / tanggal entries
            if re.search(r'backup|izin sakit|tanggal\s+\d+', name, re.IGNORECASE):
                continue
            names_list.append(name)

    print(f"  [sheets_adapter] Jadwal Shifting: {num_days} days, {len(names_list)} names")

    # ── 2. Open Insiden ─────────────────────────────────────────────────
    raw_open = baca_data(target_ss_id, tab_name="Open Insiden")
    raw_paste_open = baca_data(target_ss_id, tab_name="Paste Open Insiden")
    if raw_paste_open and len(raw_paste_open) > len(raw_open or []):
        raw_open = raw_paste_open
    if not raw_open:
        df_open = pd.DataFrame(columns=['datetime', 'nama'])
        print("  [sheets_adapter] Open Insiden: empty")
    else:
        # Check if 3 columns with "nama petugas" header
        first_row_lower = [str(v).strip().lower() for v in raw_open[0]] if raw_open else []
        if len(first_row_lower) >= 3 and 'nama petugas' in first_row_lower:
            df_open = _parse_incident_3col_all(raw_open)
        else:
            df_open = _parse_incident_sheet_from_rows(raw_open)
        print(f"  [sheets_adapter] Open Insiden: {len(df_open)} rows")

    # ── 3. Closed Insiden ───────────────────────────────────────────────
    raw_closed = baca_data(target_ss_id, tab_name="Closed Insiden")
    if not raw_closed:
        df_closed = pd.DataFrame(columns=['datetime', 'nama'])
        print("  [sheets_adapter] Closed Insiden: empty")
    else:
        first_row_lower = [str(v).strip().lower() for v in raw_closed[0]] if raw_closed else []
        if len(first_row_lower) >= 3 and 'nama petugas' in first_row_lower:
            df_closed = _parse_incident_3col_all(raw_closed)
        else:
            df_closed = _parse_incident_sheet_from_rows(raw_closed)
        print(f"  [sheets_adapter] Closed Insiden: {len(df_closed)} rows")

    # ── 4. Backup ───────────────────────────────────────────────────────
    raw_backup = baca_data(target_ss_id, tab_name="Backup")
    backup_info = []
    if raw_backup and len(raw_backup) > 1:
        # Skip header row (row 0)
        for row in raw_backup[1:]:
            try:
                day_val = int(row[0])
                col1 = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ''
                col2 = str(row[2]).strip() if len(row) > 2 and row[2] is not None else ''
                shift_val = str(row[3]).strip() if len(row) > 3 and row[3] is not None else ''

                if col2 and col2.lower() != 'nan':
                    # Format: tanggal, nama_karyawan, nama_backup, shift
                    backup_info.append({
                        'day': day_val,
                        'employee': col1,
                        'name': col2,
                        'shift': shift_val,
                    })
                elif col1 and col1.lower() != 'nan':
                    # Simple format: tanggal, nama
                    backup_info.append({
                        'day': day_val,
                        'name': col1,
                        'shift': shift_val,
                    })
            except (ValueError, TypeError, IndexError):
                continue
    print(f"  [sheets_adapter] Backup: {len(backup_info)} entries")

    # ── 5. Notes ────────────────────────────────────────────────────────
    raw_notes = baca_data(target_ss_id, tab_name="Notes")
    notes_list = []
    if raw_notes:
        for row in raw_notes:
            val = str(row[0]).strip() if row and row[0] is not None else ''
            if val and val.lower() != 'nan':
                notes_list.append(val)
    print(f"  [sheets_adapter] Notes: {len(notes_list)} entries")

    # ── Build result dict ───────────────────────────────────────────────
    result = {
        'shifts': None,           # filled later by get_shifts_for_name
        'found_name': None,       # filled later by get_shifts_for_name
        'num_days': num_days,
        'df_open': df_open,
        'df_closed': df_closed,
        'backup_info': backup_info,
        'notes_list': notes_list,
        'names_list': names_list,
        'cell_colors': ['white'] * num_days,
        # Internal: keep raw sched data for shift extraction
        '_raw_sched': raw_sched,
        # Internal: keep raw incident data for 3-col name filtering
        '_raw_open': raw_open,
        '_raw_closed': raw_closed,
    }

    return result


def _parse_incident_3col_all(rows):
    """
    Parse a 3-column incident sheet keeping ALL petugas rows (no name filter).
    This is used when we don't yet know the target name.
    
    Returns a DataFrame with columns ['datetime', 'nama', 'petugas'].
    The server will filter by petugas name when the target is selected.
    """
    if not rows:
        return pd.DataFrame(columns=['datetime', 'nama', 'petugas'])

    row0 = [str(v).strip().lower() for v in rows[0]]
    if 'nama petugas' in row0:
        petugas_idx = next(i for i, v in enumerate(row0) if v == 'nama petugas')
        other_idxs = [i for i in range(len(row0)) if i != petugas_idx]

        dt_idx = None
        insiden_idx = None
        for i in other_idxs:
            val = row0[i]
            if 'time' in val or 'date' in val or 'detected' in val or 'closed' in val:
                dt_idx = i
            elif 'insiden' in val or 'incident' in val or 'nama' in val:
                insiden_idx = i
        if dt_idx is None:
            dt_idx = other_idxs[0]
        if insiden_idx is None:
            insiden_idx = other_idxs[1] if len(other_idxs) > 1 else other_idxs[0]

        data_rows = rows[1:]
        records = []
        for row in data_rows:
            if len(row) <= max(dt_idx, insiden_idx, petugas_idx):
                continue
            dt_val = row[dt_idx]
            ins_val = row[insiden_idx] if insiden_idx < len(row) else None
            pet_val = row[petugas_idx] if petugas_idx < len(row) else None
            records.append([dt_val, ins_val, pet_val])

        df = pd.DataFrame(records, columns=['datetime', 'nama', 'petugas'])
        df['datetime'] = _smart_parse_datetime_col(df['datetime'])
        # Remove timezone info if present (core.py uses naive datetimes)
        if hasattr(df['datetime'].dtype, 'tz') and df['datetime'].dtype.tz is not None:
            df['datetime'] = df['datetime'].dt.tz_localize(None)
        df['nama'] = df['nama'].apply(lambda x: str(x).strip() if x is not None else '')
        df['petugas'] = df['petugas'].apply(lambda x: str(x).strip() if x is not None else '')
        df = df.dropna(subset=['datetime'])
        return df
    else:
        # Fall back to 2-col parse
        return _parse_incident_sheet_from_rows(rows)


def get_shifts_for_name(sheets_data, target_name):
    """
    Given the sheets_data dict (from build_dataframes) and a target_name,
    extract the shift values for that employee and set the found_name.
    
    Also re-parses df_open and df_closed if they have 3-column 'nama petugas'
    format, filtering by the target name.
    
    Returns the updated sheets_data dict with 'shifts' and 'found_name' filled.
    """
    raw_sched = sheets_data['_raw_sched']
    names_list = sheets_data['names_list']

    # Find the target row
    found_name = None
    target_row_idx = None
    for row_idx in range(2, len(raw_sched)):
        name = str(raw_sched[row_idx][0]).strip() if raw_sched[row_idx] and raw_sched[row_idx][0] is not None else ''
        if name and match_employee_name(name, target_name):
            found_name = name
            target_row_idx = row_idx
            break

    if found_name is None:
        raise ValueError(f"Nama '{target_name}' tidak ditemukan di jadwal shifting.")

    # Extract shifts
    num_days = sheets_data['num_days']
    row_data = raw_sched[target_row_idx]
    shifts = []
    for col_idx in range(1, num_days + 1):
        if col_idx < len(row_data):
            shifts.append(row_data[col_idx])
        else:
            shifts.append('')  # missing column → empty shift

    # Update sheets_data
    sheets_data['shifts'] = shifts
    sheets_data['found_name'] = found_name

    # ── If incident sheets have 3-col 'nama petugas' format, filter by name ──
    raw_open = sheets_data.get('_raw_open', [])
    if raw_open:
        first_row_lower = [str(v).strip().lower() for v in raw_open[0]]
        if len(first_row_lower) >= 3 and 'nama petugas' in first_row_lower:
            df_open = _parse_incident_3col(raw_open, found_name)
            sheets_data['df_open'] = df_open

    raw_closed = sheets_data.get('_raw_closed', [])
    if raw_closed:
        first_row_lower = [str(v).strip().lower() for v in raw_closed[0]]
        if len(first_row_lower) >= 3 and 'nama petugas' in first_row_lower:
            df_closed = _parse_incident_3col(raw_closed, found_name)
            sheets_data['df_closed'] = df_closed

    # ── Filter backup_info by target name (for 3/4 col format) ──
    backup_info_filtered = []
    for info in sheets_data.get('backup_info', []):
        if 'employee' in info:
            # 4-col format: only keep if employee matches target
            if match_employee_name(info['employee'], found_name) or match_employee_name(info['employee'], target_name):
                backup_info_filtered.append({'day': info['day'], 'name': info['name'], 'shift': info.get('shift', '')})
        else:
            # 2-col format: keep all (simple day+name)
            backup_info_filtered.append(info)
    sheets_data['backup_info'] = backup_info_filtered

    return sheets_data
