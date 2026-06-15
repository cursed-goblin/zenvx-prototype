from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .commands import runner
from .utils import WINE_PREFIXES_DIR, slugify, MOCK


@dataclass
class WindowsInstallResult:
    prefix_path: Path
    notes: str


class WindowsAdapter:
    runtime = "windows"

    def is_installed(self) -> bool:
        if MOCK: return True
        return runner.run(["which", "wine"], timeout_s=10).returncode == 0

    def init_prefix(self, app_slug: str) -> Path:
        prefix = WINE_PREFIXES_DIR / app_slug
        prefix.mkdir(parents=True, exist_ok=True)
        if MOCK: return prefix
        r = runner.run(["wineboot", "--init"], env={"WINEPREFIX": str(prefix)}, timeout_s=300, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
        return prefix

    def install_exe(self, exe_path: Path, display_name: str) -> WindowsInstallResult:
        app_slug = slugify(display_name)
        prefix = self.init_prefix(app_slug)
        if MOCK: return WindowsInstallResult(prefix_path=prefix, notes="mock install")
        r = runner.run(["wine", str(exe_path)], env={"WINEPREFIX": str(prefix)}, timeout_s=3600, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
        return WindowsInstallResult(prefix_path=prefix, notes="installer executed")

    def launch_exe(self, prefix: Path, windows_path: str) -> None:
        if MOCK: return
        r = runner.run(["wine", windows_path], env={"WINEPREFIX": str(prefix)}, timeout_s=3600, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
