"""
config.py
---------
Single Source of Truth untuk konfigurasi, konstanta, dan pengaturan lingkungan
pada proyek Timesheet Cleaner Spreadsheet.
Menggunakan pydantic-settings untuk membaca dari environment variables atau file .env.
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── Path & Directory Settings ──────────────────────────────────────────
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)
    upload_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "uploads")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "output")

    # ── Server Settings ────────────────────────────────────────────────────
    server_host: str = "0.0.0.0"
    server_port: int = 8769
    log_file: str = "server.log"

    # ── Google Sheets & Apps Script Adapter Settings ───────────────────────
    web_app_url: str = "https://script.google.com/macros/s/AKfycbwcjKNwfeJiCwa6Qx1Xd1bI43tkV_a82UHfl70cvpa1J7AYXXvE0eB8kdQBByb19PnJFQ/exec"
    timesheet_ss_id: str = ""

    @field_validator("timesheet_ss_id", mode="before")
    @classmethod
    def clean_ss_id(cls, v: str) -> str:
        if not v:
            return ""
        val = str(v).strip()
        m = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', val)
        if m:
            return m.group(1)
        return val

    # ── Node.js DOCX Generator Settings ────────────────────────────────────
    docx_script_name: str = "generate_docx.js"
    node_candidates: List[str] = [
        "/home/homelinux/.hermes/node/bin/node",
        "/home/homelinux/.nvm/versions/node/v20.20.2/bin/node",
        "/home/homelinux/.local/bin/node",
        "/usr/bin/node",
    ]

    # ── Constants & Lookup Tables ──────────────────────────────────────────
    month_names_id: List[str] = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    normalization_map: Dict[str, str] = {
        "UNCONFIRMED": "UNCONFIRM",
        "UNICONFIRM": "UNCONFIRM",
        "DISMANTEL": "DISMANTLE",
        "APLIKASI EROR": "APLIKASI ERROR",
    }

    typo_map: Dict[str, str] = {
        "UNFONFIRM": "UNCONFIRM",
        "UNCONFIRMED": "UNCONFIRM",
        "UNCOINFIRM": "UNCONFIRM",
        "UNCOMFIRM": "UNCONFIRM",
        "UNCONFRIM": "UNCONFIRM",
        "UNCONFIRMSATKOM": "UNCONFIRM",
        "POWER ELECTRCITY": "POWER ELECTRICITY",
        "POWER ELETRICITY": "POWER ELECTRICITY",
        "POWER ELECTRICTY": "POWER ELECTRICITY",
        "POWER ELECTRCTY": "POWER ELECTRICITY",
        "DISMANTTEL": "DISMANTLE",
        "DISMANTTLE": "DISMANTLE",
        "JAKROM LASTMILE": "JARKOM LASTMILE",
        "APLIKAS ERROR": "APLIKASI ERROR",
        "APLIKASI": "APLIKASI ERROR",
        "ROUTING GPRS": "REQUEST ROUTING",
        "REQ ROUTING VSAT": "REQUEST ROUTING",
        "REQ BACKUP PSB": "REQUEST ROUTING",
        "REQ ROUTING": "REQUEST ROUTING",
        "REQ ROUTING CELLULER": "REQUEST ROUTING",
        "REQ ROUTING EBUZZ": "REQUEST ROUTING",
        "ROUTING": "REQUEST ROUTING",
        "REQUEST ROUTING": "REQUEST ROUTING",
        "REQUEST ROUTING VSAT": "REQUEST ROUTING",
        "REQUEST ROUTING CELLULER": "REQUEST ROUTING",
        "REQUEST ROUTING EBUZZ": "REQUEST ROUTING",
        "REQUEST BACKUP PSB": "REQUEST ROUTING",
        "JARINGAN LAMBAT": "JARKOM LAMBAT",
        "DOUBLE TIKET": "UNCONFIRM",
        "DOUBLE TICKET": "UNCONFIRM",
        "OFFINE": "OFFLINE",
        "VANDALISM": "VANDALISME",
        "VANDALISME": "VANDALISME",
        "BUILDING RENOVATION": "BUILDING RENOVATION",
        "BUILDING RENOVASI": "BUILDING RENOVATION",
    }

    # ── Shift Definitions (Configuration-Driven Pattern) ───────────────────
    shift_definitions: Dict[str, Dict[str, str]] = {
        "1": {"type": "S1", "start": "06:00", "end": "15:00", "remark": "Shift 1"},
        "2": {"type": "S2", "start": "14:00", "end": "23:00", "remark": "Shift 2"},
        "3": {"type": "S3", "start": "22:00", "end": "07:00", "remark": "Shift 3"},
        "1.2": {"type": "S12", "start": "06:00", "end": "23:00", "remark": "Shift 1 & Shift 2"},
        "2.3": {"type": "S23", "start": "14:00", "end": "07:00", "remark": "Shift 2 & Shift 3"},
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def docx_script_path(self) -> Path:
        return self.base_dir / self.docx_script_name

    def get_node_bin(self) -> str:
        """Mencari binary Node.js yang valid di sistem atau daftar kandidat."""
        system_node = shutil.which("node")
        if system_node:
            return system_node
        for path_str in self.node_candidates:
            p = Path(path_str)
            if p.exists() and p.is_file():
                return path_str
        return "node"


settings = Settings()
