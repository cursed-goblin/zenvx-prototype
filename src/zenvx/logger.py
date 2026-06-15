from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .utils import LOG_DIR, ensure_dirs, now_ts


@dataclass
class Logger:
    path: Path
    max_bytes: int = 2_000_000

    def _rotate(self) -> None:
        if self.path.exists() and self.path.stat().st_size > self.max_bytes:
            bak = self.path.with_suffix(self.path.suffix + ".1")
            try:
                if bak.exists():
                    bak.unlink()
                self.path.rename(bak)
            except Exception:
                pass

    def _write(self, level: str, runtime: str, app_id: str, msg: str) -> None:
        ensure_dirs()
        self._rotate()
        rec = {"ts": now_ts(), "level": level, "runtime": runtime, "app_id": app_id, "msg": msg}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def info(self, runtime: str, app_id: str, msg: str) -> None:
        self._write("INFO", runtime, app_id, msg)

    def warn(self, runtime: str, app_id: str, msg: str) -> None:
        self._write("WARN", runtime, app_id, msg)

    def error(self, runtime: str, app_id: str, msg: str) -> None:
        self._write("ERROR", runtime, app_id, msg)

    def debug(self, runtime: str, app_id: str, msg: str) -> None:
        self._write("DEBUG", runtime, app_id, msg)


logger = Logger(path=LOG_DIR / "zenvx.log")
