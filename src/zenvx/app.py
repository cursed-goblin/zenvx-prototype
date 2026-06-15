from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .android import AndroidAdapter
from .appimage import AppImageAdapter
from .desktop import DesktopEntry, write_desktop_entry
from .registry import AppRecord, Registry
from .rpm import RPMAdapter
from .universal import detect_file
from .utils import ensure_dirs, now_ts, slugify
from .windows import WindowsAdapter


@dataclass
class InstallPreview:
    kind: str
    display_name: str
    warnings: list[str]
    metadata: Dict[str, Any]


class ZenvXApp:
    def __init__(self) -> None:
        ensure_dirs()
        self.registry = Registry()
        self.android = AndroidAdapter()
        self.windows = WindowsAdapter()
        self.appimage = AppImageAdapter()
        self.rpm = RPMAdapter()

    def preview_install(self, path: Path) -> InstallPreview:
        det = detect_file(path)
        warnings: list[str] = []
        meta: Dict[str, Any] = {"detected_reason": det.reason}
        if det.kind == "unknown": warnings.append("Unknown file type; install disabled.")
        if det.kind == "rpm": warnings.append("RPM support is experimental on Debian.")
        if det.kind == "exe": warnings.append("Wine cannot run all Windows apps.")
        if det.kind == "apk": warnings.append("Waydroid may need initialization/session and may require sudo.")
        return InstallPreview(det.kind, path.stem, warnings, meta)

    def install(self, path: Path, display_name: Optional[str] = None, allow_sudo: bool = False) -> str:
        prev = self.preview_install(path)
        if prev.kind == "unknown": raise ValueError("Unknown file type")

        name = display_name or prev.display_name
        app_id = slugify(name)
        ts = now_ts()

        runtime_type = prev.kind
        package_or_binary = ""
        launch_target = ""
        wine_prefix_path = ""
        rpm_rootfs_path = ""
        appimage_path = ""

        if prev.kind == "apk":
            package_or_binary = self.android.install(path, allow_sudo=allow_sudo)
            launch_target = package_or_binary
        elif prev.kind == "exe":
            res = self.windows.install_exe(path, name)
            wine_prefix_path = str(res.prefix_path)
            package_or_binary = path.name
        elif prev.kind == "appimage":
            res = self.appimage.install(path, name)
            appimage_path = str(res.appimage_path)
            launch_target = str(res.appimage_path)
            prev.metadata["appimage_extract_and_run"] = res.extract_and_run
        elif prev.kind == "rpm":
            res = self.rpm.install(path, name)
            rpm_rootfs_path = str(res.rootfs)
            prev.metadata["rpm_mode"] = res.mode
            prev.metadata["rpm_candidates"] = res.candidates
            launch_target = res.candidates[0] if res.candidates else ""
            package_or_binary = path.name

        entry = DesktopEntry(
            name=name,
            comment=f"ZenvX ({runtime_type})",
            exec_cmd=f"zenvx launch {app_id}",
            icon="application-x-executable",
            runtime=runtime_type,
            app_id=app_id,
        )
        desktop_path = write_desktop_entry(app_id, entry)

        rec = AppRecord(
            app_id=app_id,
            runtime_type=runtime_type,
            source_type=prev.kind,
            display_name=name,
            package_or_binary=package_or_binary,
            launch_target=launch_target,
            install_path="",
            icon_path="",
            wine_prefix_path=wine_prefix_path,
            rpm_rootfs_path=rpm_rootfs_path,
            appimage_path=appimage_path,
            desktop_entry_path=str(desktop_path),
            compatibility_status="unknown",
            compatibility_score=None,
            metadata_json=prev.metadata,
            last_launch_timestamp=None,
            created_timestamp=ts,
            updated_timestamp=ts,
        )
        self.registry.add_app(rec)
        return app_id

    def launch(self, app_id: str, allow_sudo: bool = False) -> None:
        rec = self.registry.get_app(app_id)
        if not rec: raise KeyError(app_id)

        if rec.runtime_type == "apk":
            self.android.launch(rec.launch_target, allow_sudo=allow_sudo)
        elif rec.runtime_type == "exe":
            raise ValueError("Windows launch target is not auto-detected in this prototype build")
        elif rec.runtime_type == "appimage":
            extract = bool(rec.metadata_json.get("appimage_extract_and_run", False))
            self.appimage.launch(Path(rec.launch_target), extract_and_run=extract)
        elif rec.runtime_type == "rpm":
            self.rpm.launch(Path(rec.rpm_rootfs_path), rec.launch_target)
        else:
            raise ValueError(rec.runtime_type)

        self.registry.update_last_launch(app_id)

    def remove(self, app_id: str, *, confirm: bool = False, allow_sudo: bool = False) -> None:
        if not confirm: raise PermissionError("Removal requires confirm=True")
        rec = self.registry.get_app(app_id)
        if not rec: return
        if rec.runtime_type == "apk" and rec.launch_target:
            self.android.remove(rec.launch_target, allow_sudo=allow_sudo)
        try:
            if rec.desktop_entry_path:
                Path(rec.desktop_entry_path).unlink(missing_ok=True)
        except Exception:
            pass
        self.registry.remove_app(app_id)
