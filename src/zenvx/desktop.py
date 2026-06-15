from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .utils import DESKTOP_DIR


@dataclass
class DesktopEntry:
    name: str
    comment: str
    exec_cmd: str
    icon: str
    categories: str = "Utility;"
    startup_wm_class: str = ""
    runtime: str = ""
    app_id: str = ""

    def render(self) -> str:
        lines = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={self.name}",
            f"Comment={self.comment}",
            f"Exec={self.exec_cmd}",
            f"Icon={self.icon}",
            f"Categories={self.categories}",
            "Terminal=false",
            "StartupNotify=true",
        ]
        if self.startup_wm_class:
            lines.append(f"StartupWMClass={self.startup_wm_class}")
        if self.runtime:
            lines.append(f"X-ZenvX-Runtime={self.runtime}")
        if self.app_id:
            lines.append(f"X-ZenvX-AppID={self.app_id}")
        return "\n".join(lines) + "\n"


def write_desktop_entry(app_id: str, entry: DesktopEntry) -> Path:
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    path = DESKTOP_DIR / f"zenvx-{app_id}.desktop"
    path.write_text(entry.render(), encoding="utf-8")
    return path
