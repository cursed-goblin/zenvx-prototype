from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import DB_PATH, ensure_dirs, now_ts


@dataclass
class AppRecord:
    app_id: str
    runtime_type: str
    source_type: str
    display_name: str
    package_or_binary: str
    launch_target: str
    install_path: str
    icon_path: str
    wine_prefix_path: str
    rpm_rootfs_path: str
    appimage_path: str
    desktop_entry_path: str
    compatibility_status: str
    compatibility_score: Optional[int]
    metadata_json: Dict[str, Any]
    last_launch_timestamp: Optional[int]
    created_timestamp: int
    updated_timestamp: int


class Registry:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        ensure_dirs()
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _migrate(self) -> None:
        con = self._connect()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS apps (
                    app_id TEXT PRIMARY KEY,
                    runtime_type TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    package_or_binary TEXT,
                    launch_target TEXT,
                    install_path TEXT,
                    icon_path TEXT,
                    wine_prefix_path TEXT,
                    rpm_rootfs_path TEXT,
                    appimage_path TEXT,
                    desktop_entry_path TEXT,
                    compatibility_status TEXT,
                    compatibility_score INTEGER,
                    metadata_json TEXT,
                    last_launch_timestamp INTEGER,
                    created_timestamp INTEGER NOT NULL,
                    updated_timestamp INTEGER NOT NULL
                )
            """)
            con.commit()
        finally:
            con.close()

    def add_app(self, rec: AppRecord) -> None:
        con = self._connect()
        try:
            con.execute("""INSERT OR REPLACE INTO apps(
                app_id,runtime_type,source_type,display_name,package_or_binary,launch_target,
                install_path,icon_path,wine_prefix_path,rpm_rootfs_path,appimage_path,desktop_entry_path,
                compatibility_status,compatibility_score,metadata_json,last_launch_timestamp,created_timestamp,updated_timestamp
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rec.app_id,rec.runtime_type,rec.source_type,rec.display_name,rec.package_or_binary,rec.launch_target,
             rec.install_path,rec.icon_path,rec.wine_prefix_path,rec.rpm_rootfs_path,rec.appimage_path,rec.desktop_entry_path,
             rec.compatibility_status,rec.compatibility_score,json.dumps(rec.metadata_json,ensure_ascii=False),rec.last_launch_timestamp,
             rec.created_timestamp,rec.updated_timestamp))
            con.commit()
        finally:
            con.close()

    def remove_app(self, app_id: str) -> None:
        con = self._connect()
        try:
            con.execute("DELETE FROM apps WHERE app_id=?", (app_id,))
            con.commit()
        finally:
            con.close()

    def get_app(self, app_id: str) -> Optional[AppRecord]:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM apps WHERE app_id=?", (app_id,)).fetchone()
            return self._row(row) if row else None
        finally:
            con.close()

    def list_apps(self) -> List[AppRecord]:
        con = self._connect()
        try:
            rows = con.execute("SELECT * FROM apps ORDER BY updated_timestamp DESC").fetchall()
            return [self._row(r) for r in rows]
        finally:
            con.close()

    def search_apps(self, q: str) -> List[AppRecord]:
        con = self._connect()
        try:
            like = f"%{q}%"
            rows = con.execute("SELECT * FROM apps WHERE display_name LIKE ? OR app_id LIKE ?", (like, like)).fetchall()
            return [self._row(r) for r in rows]
        finally:
            con.close()

    def update_last_launch(self, app_id: str) -> None:
        con = self._connect()
        try:
            con.execute("UPDATE apps SET last_launch_timestamp=?, updated_timestamp=? WHERE app_id=?", (now_ts(), now_ts(), app_id))
            con.commit()
        finally:
            con.close()

    def export_registry_json(self) -> str:
        return json.dumps({"apps": [a.__dict__ for a in self.list_apps()]}, ensure_ascii=False, indent=2)

    def _row(self, row: sqlite3.Row) -> AppRecord:
        return AppRecord(
            app_id=row["app_id"],
            runtime_type=row["runtime_type"],
            source_type=row["source_type"],
            display_name=row["display_name"],
            package_or_binary=row["package_or_binary"] or "",
            launch_target=row["launch_target"] or "",
            install_path=row["install_path"] or "",
            icon_path=row["icon_path"] or "",
            wine_prefix_path=row["wine_prefix_path"] or "",
            rpm_rootfs_path=row["rpm_rootfs_path"] or "",
            appimage_path=row["appimage_path"] or "",
            desktop_entry_path=row["desktop_entry_path"] or "",
            compatibility_status=row["compatibility_status"] or "unknown",
            compatibility_score=row["compatibility_score"],
            metadata_json=json.loads(row["metadata_json"] or "{}"),
            last_launch_timestamp=row["last_launch_timestamp"],
            created_timestamp=row["created_timestamp"],
            updated_timestamp=row["updated_timestamp"],
        )
