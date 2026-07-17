# Timesheet Cleaner & DOCX Generator 📊✨

Aplikasi berbasis web (FastAPI & Node.js) untuk membersihkan, memproses, dan merangkum data rekap aktivitas konsultan dari **Google Sheets** atau file **Excel**, serta menghasilkan laporan dokumen **DOCX** secara otomatis dan terstruktur.

---

## 🚀 Fitur Utama

- **Integrasi Google Sheets Dinamis**: Memuat data rekap bulanan langsung dari Google Spreadsheet dengan memasukkan link URL/ID tanpa mengedit kode source.
- **Dukungan Upload Excel (.xlsx)**: Opsi alternatif untuk mengunggah file spreadsheet Excel secara langsung dari browser.
- **Pemrosesan Otomatis (Jadwal, Insiden & Backup)**:
  - Ekstraksi jadwal shift konsultan secara otomatis per hari.
  - Pengelompokan dan normalisasi judul insiden (Open & Closed).
  - Pengecekan status *Backup* dan *Notes* harian.
- **Export Laporan DOCX**: Menggunakan *templating* Node.js (`docx`) untuk menghasilkan laporan bulanan berformat rapi siap cetak/kirim.
- **Antarmuka Web Modern (UI/UX)**: Tampilan dasbor bergaya kaca (*glassmorphism*) yang responsif dengan *real-time feedback*.

---

## 📁 Struktur Proyek

```text
├── config.py             # Pengaturan konfigurasi dinamis (Pydantic Settings)
├── core.py               # Logika inti pemrosesan data spreadsheet & normalisasi
├── sheets_adapter.py     # Adaptor koneksi & pembacaan tab Google Sheets via Apps Script
├── server.py             # Server backend FastAPI & definisi *endpoints* API
├── index.html            # Antarmuka web pengguna (UI)
├── generate_docx.js      # Generator dokumen DOCX berbasis Node.js
├── requirements.txt      # Daftar dependensi Python
├── .env.example          # Template konfigurasi environment (URL/ID Google Sheets)
└── .gitignore            # Konfigurasi pengabaian file untuk Git
```

---

## 🛠️ Prasyarat & Instalasi

### 1. Prasyarat Sistem
- **Python 3.10+**
- **Node.js 18+** (untuk pembuatan dokumen DOCX)

### 2. Instalasi Dependensi

1. Clone repositori ini dan masuk ke direktori proyek:
   ```bash
   git clone <URL_REPO_GITHUB_ANDA>
   cd timesheet-cleaner-spreadsheet-dev
   ```

2. Buat virtual environment Python dan pasang dependensi:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Untuk Linux/macOS
   # atau .venv\Scripts\activate untuk Windows
   
   pip install -r requirements.txt
   ```

3. Pasang dependensi Node.js untuk generator DOCX:
   ```bash
   npm install
   ```

---

## ⚙️ Cara Memuat Spreadsheet Bulanan (100% Dinamis dari UI Web)

Proyek ini telah dirancang sepenuhnya dinamis sehingga link Google Spreadsheet bulanan **tidak lagi ditanam (hardcode) di dalam kode program maupun file konfigurasi**.

Anda memiliki **2 Pilihan Cara Memuat Data Spreadsheet**:

### 🌟 Cara Utama (Direkomendasikan): Langsung via Halaman Web UI (`index.html`)
Setiap bulan saat link spreadsheet berganti, Anda **tidak perlu mengedit file apa pun (`.env` ataupun kode python)**.
1. Buka dasbor web di browser (`http://localhost:8769`).
2. Tempelkan link URL Google Spreadsheet bulan terbaru pada kotak input **"Masukan Link Google Spreadsheet nya"**.
3. Klik tombol **Load from Google Sheets**. Sistem otomatis mengekstrak ID dan langsung memuat data terbaru secara *real-time*!

### ⚙️ Cara Alternatif (Opsional untuk Server Admin): via File `.env`
Jika Anda ingin link tertentu dimuat secara otomatis sebagai default tanpa perlu input di UI setiap kali server direstart:
1. Salin template `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
2. Isi nilai `TIMESHEET_SS_ID=https://docs.google.com/spreadsheets/d/...` pada file `.env` tersebut.

---

## ▶️ Menjalankan Aplikasi

Jalankan server FastAPI menggunakan `uvicorn` atau langsung melalui Python:

```bash
uvicorn server:app --host 0.0.0.0 --port 8769 --reload
# atau
python3 server.py
```

Buka browser dan akses dasbor web pada URL:
👉 **http://localhost:8769**

---

## 📖 Panduan Penggunaan Singkat

1. **Langkah 1 (Muat Spreadsheet)**:
   - Tempelkan link URL Google Spreadsheet terbaru Anda pada kotak input di halaman dasbor, lalu klik **Load from Google Sheets**.
   - *(Atau biarkan kosong dan klik tombol tersebut jika sudah mengatur `TIMESHEET_SS_ID` pada file `.env`).*
2. **Langkah 2 (Pilih Konsultan)**:
   - Pilih nama konsultan dari *dropdown list* yang otomatis terdeteksi dari tab *Jadwal Shifting*.
3. **Langkah 3 (Proses & Export)**:
   - Klik tombol **Process & Preview Data** untuk melihat ringkasan shift dan insiden.
   - Klik **Download Laporan DOCX** untuk mengunduh laporan akhir berformat Word (`.docx`).

---

## 🔒 Keamanan & Praktik Terbaik

- **Jangan pernah meng-commit file `.env`** yang berisi data sensitif atau kredensial internal ke repositori publik. File `.env` sudah dimasukkan ke dalam `.gitignore`.
- Folder `uploads/` dan `output/` hanya digunakan untuk penyimpanan sementara saat pemrosesan berlangsung.
