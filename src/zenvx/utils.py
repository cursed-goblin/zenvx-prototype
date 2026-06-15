from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

APP_NAME = "ZenvX"
MODULE_PREFIX = "zenvx"

def _default_data_dir() -> Path:
    # Debian-friendly default: ~/.local/share/ZenvX
    home = Path.home()
    xdg_data_home = Path(os.environ.get("XDG_DATA_HOME", str(home / ".local/share")))
    return xdg_data_home / APP_NAME


DATA_DIR = Path(os.environ.get("ZENVX_DATA_DIR", str(_default_data_dir())))
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "zenvx.sqlite"
WINE_PREFIXES_DIR = DATA_DIR / "wine-prefixes"
APPIMAGES_DIR = DATA_DIR / "appimages"
RPM_ROOTS_DIR = DATA_DIR / "rpm-roots"

DESKTOP_DIR = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "applications"
ZENVX_DESKTOP_ENTRY_PATH = DESKTOP_DIR / "zenvx.desktop"

MOCK = os.environ.get("ZENVX_MOCK") == "1" or os.environ.get("COMPATOS_MOCK") == "1"


def ensure_dirs() -> None:
    for p in [DATA_DIR, LOG_DIR, WINE_PREFIXES_DIR, APPIMAGES_DIR, RPM_ROOTS_DIR, DESKTOP_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def now_ts() -> int:
    return int(time.time())


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "app"


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    fix: Optional[str] = None
