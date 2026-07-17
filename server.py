"""
server.py — FastAPI backend for Timesheet Cleaner dashboard.
Serves the HTML UI and handles Excel upload, processing, and DOCX generation.

Fixes applied vs original:
- BUG-02:   Semua logika pemrosesan dipindahkan ke core.py (tidak ada duplikasi)
- ISSUE-04: Upload file lama dibersihkan otomatis sebelum menyimpan file baru
"""

import json
import re
import subprocess
import shutil
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# ── BUG-02 FIX: Import semua logika dari core.py (tidak ada duplikasi kode) ──
from core import process_excel, process_from_sheets_data
import sheets_adapter
from config import settings

# ── Config ─────────────────────────────────────────────────────────────────
BASE_DIR   = settings.base_dir
UPLOAD_DIR = settings.upload_dir
OUTPUT_DIR = settings.output_dir
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Cache for Google Sheets data (between load-from-sheets and process calls) ──
_sheets_data_cache = None

app = FastAPI(title="Timesheet Cleaner")

# ── Error handlers ─────────────────────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    err_str = str(exc).lower()
    if any(kw in err_str for kw in ['broken pipe', 'client disconnected', 'connection reset', 'write aborted']):
        logging.getLogger(__name__).warning(f"Client disconnected during request: {request.url.path}")
        return JSONResponse(status_code=499, content={"detail": "Client disconnected"})
    logging.getLogger(__name__).error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = BASE_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding='utf-8'))


# ============================================================
# [DISABLED: EXCEL UPLOAD OPTION]
# Untuk mengaktifkan kembali fitur upload Excel (.xlsx/.xls),
# uncomment blok fungsi @app.post("/api/upload") di bawah ini:
# ============================================================
# @app.post("/api/upload")
# async def upload_excel(file: UploadFile = File(...)):
#     """Upload Excel file and return available names."""
#     if not file.filename.endswith(('.xlsx', '.xls')):
#         raise HTTPException(400, "File harus berformat .xlsx atau .xls")
# 
#     # ISSUE-04 FIX: Hapus semua file lama di uploads/ sebelum menyimpan yang baru
#     for old_file in UPLOAD_DIR.iterdir():
#         if old_file.is_file():
#             try:
#                 old_file.unlink()
#             except Exception:
#                 pass
# 
#     # Save uploaded file
#     save_path = UPLOAD_DIR / file.filename
#     with open(save_path, 'wb') as f:
#         content = await file.read()
#         f.write(content)
# 
#     try:
#         names, _ = process_excel(str(save_path))
#     except Exception as e:
#         raise HTTPException(400, f"Gagal membaca Excel: {str(e)}")
# 
#     return JSONResponse({
#         "filename": file.filename,
#         "names": names,
#         "message": f"File berhasil diupload. Ditemukan {len(names)} nama."
#     })


@app.post("/api/load-from-sheets")
async def load_from_sheets(sheet_id: str = Form(None)):
    """Load timesheet data from Google Sheets and return available names."""
    global _sheets_data_cache

    val = sheet_id.strip() if (sheet_id and sheet_id.strip()) else settings.timesheet_ss_id
    if not val or not str(val).strip():
        raise HTTPException(400, "Silakan masukkan link URL atau ID Google Spreadsheet di kolom input UI (atau isi TIMESHEET_SS_ID pada file .env).")

    val = str(val).strip()
    m = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', val)
    if m:
        target_ss_id = m.group(1)
    else:
        target_ss_id = val

    try:
        sheets_data = sheets_adapter.build_dataframes(ss_id=target_ss_id)
        _sheets_data_cache = sheets_data
    except Exception as e:
        raise HTTPException(400, f"Gagal membaca Google Sheets: {str(e)}")

    names = sheets_data['names_list']
    return JSONResponse({
        "names": names,
        "message": f"Data Google Sheets berhasil dimuat. Ditemukan {len(names)} nama.",
        "source": "sheets"
    })


@app.post("/api/process")
async def process_data(filename: str = Form(None), name: str = Form(...), source: str = Form(None)):
    """Process timesheet data for selected name.
    Uses Google Sheets cache if requested or if no filename provided, otherwise uses Excel upload."""
    global _sheets_data_cache

    use_sheets = (source == 'sheets') or (not filename and _sheets_data_cache is not None)

    if use_sheets:
        if _sheets_data_cache is None:
            raise HTTPException(400, "Data Google Sheets belum dimuat. Klik 'Load from Google Sheets' terlebih dahulu.")
        try:
            sheets_data = sheets_adapter.get_shifts_for_name(_sheets_data_cache, name)
            names, output = process_from_sheets_data(sheets_data, name)
        except Exception as e:
            raise HTTPException(400, f"Gagal memproses (Google Sheets): {str(e)}")
    else:
        if not filename:
            raise HTTPException(400, "Tidak ada data. Upload file Excel atau load dari Google Sheets dulu.")
        excel_path = UPLOAD_DIR / filename
        if not excel_path.exists():
            raise HTTPException(404, "File tidak ditemukan. Upload ulang file Excel.")

        try:
            names, output = process_excel(str(excel_path), name)
        except Exception as e:
            raise HTTPException(400, f"Gagal memproses file Excel: {str(e)}")

    # Save JSON output
    safe_name = output['employee_name'].replace(' ', '_')
    json_filename = f"timesheet_{safe_name}.json"
    json_path = OUTPUT_DIR / json_filename
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return JSONResponse({
        "json_filename": json_filename,
        "data": output,
        "message": f"Data {output['employee_name']} berhasil diproses."
    })


@app.post("/api/generate-docx")
async def generate_docx(json_filename: str = Form(...)):
    """Generate DOCX from processed JSON data."""
    json_path = OUTPUT_DIR / json_filename
    if not json_path.exists():
        raise HTTPException(404, "Data JSON tidak ditemukan. Proses dulu.")

    docx_filename = json_filename.replace('.json', '.docx')
    docx_path     = OUTPUT_DIR / docx_filename
    js_script     = BASE_DIR / "generate_docx.js"
    NODE_BIN      = settings.get_node_bin()
    try:
        result = subprocess.run(
            [NODE_BIN, str(js_script), '--input', str(json_path), '--output', str(docx_path)],
            capture_output=True, text=True, timeout=30, cwd=str(BASE_DIR)
        )
        if result.returncode != 0:
            raise HTTPException(500, f"Gagal generate DOCX: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Timeout generating DOCX")

    if not docx_path.exists():
        raise HTTPException(500, "DOCX file tidak terbuat.")

    return FileResponse(
        path=str(docx_path),
        filename=docx_filename,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


@app.post("/api/download-json")
async def download_json(json_filename: str = Form(...)):
    """Download the processed JSON file."""
    json_path = OUTPUT_DIR / json_filename
    if not json_path.exists():
        raise HTTPException(404, "File JSON tidak ditemukan.")
    return FileResponse(path=str(json_path), filename=json_filename, media_type='application/json')


if __name__ == '__main__':
    import uvicorn
    from logging.handlers import RotatingFileHandler

    log_path = BASE_DIR / "server.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3),
            logging.StreamHandler(),
        ]
    )

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8768,
        log_level='info',
        timeout_keep_alive=30,
    )
