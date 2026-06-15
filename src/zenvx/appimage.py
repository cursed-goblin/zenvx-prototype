from __future__ import annotations

import stat
from dataclasses import dataclass
from pathlib import Path

from .commands import runner
from .utils import APPIMAGES_DIR, slugify, MOCK


@dataclass
class AppImageInstallResult:
    appimage_path: Path
    extract_and_run: bool


class AppImageAdapter:
    runtime = "appimage"

    def is_libfuse2_installed(self) -> bool:
        if MOCK: return True
        r = runner.run(["dpkg", "-s", "libfuse2"], timeout_s=10, runtime=self.runtime)
        return r.returncode == 0

    def install(self, appimage_path: Path, display_name: str) -> AppImageInstallResult:
        app_slug = slugify(display_name)
        target_dir = APPIMAGES_DIR / app_slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / appimage_path.name
        if not MOCK:
            target.write_bytes(appimage_path.read_bytes())
            target.chmod(target.stat().st_mode | stat.S_IXUSR)
        extract = not self.is_libfuse2_installed()
        return AppImageInstallResult(appimage_path=target, extract_and_run=extract)

    def launch(self, installed_path: Path, *, extract_and_run: bool) -> None:
        if MOCK: return
        env = {"APPIMAGE_EXTRACT_AND_RUN": "1"} if extract_and_run else None
        r = runner.run([str(installed_path)], env=env, timeout_s=3600, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
