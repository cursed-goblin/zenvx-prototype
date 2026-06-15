from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .commands import runner
from .utils import MOCK


@dataclass
class AndroidMetadata:
    package_name: str
    label: str


class AndroidAdapter:
    runtime = "android"

    def is_installed(self) -> bool:
        if MOCK: return True
        return runner.run(["which", "waydroid"], timeout_s=10).returncode == 0

    def extract_metadata(self, apk_path: Path) -> AndroidMetadata:
        if MOCK: return AndroidMetadata(package_name="com.example.mock", label=apk_path.stem)
        for tool in ("aapt2", "aapt"):
            if runner.run(["which", tool], timeout_s=10).returncode == 0:
                r = runner.run([tool, "dump", "badging", str(apk_path)], timeout_s=30, runtime=self.runtime)
                pkg = ""
                label = apk_path.stem
                for line in (r.stdout or "").splitlines():
                    if line.startswith("package: ") and "name='" in line:
                        pkg = line.split("name='")[1].split("'")[0]
                    if line.startswith("application-label:"):
                        label = line.split(":", 1)[1].strip().strip("'")
                if pkg: return AndroidMetadata(package_name=pkg, label=label)
        return AndroidMetadata(package_name="", label=apk_path.stem)

    def install(self, apk_path: Path, *, allow_sudo: bool = False) -> str:
        if MOCK: return "com.example.mock"
        r = runner.run(["waydroid", "app", "install", str(apk_path)], timeout_s=300, allow_sudo=allow_sudo, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
        return self.extract_metadata(apk_path).package_name

    def list_apps(self) -> List[str]:
        if MOCK: return ["com.example.mock"]
        r = runner.run(["waydroid", "app", "list"], timeout_s=60, runtime=self.runtime)
        if r.returncode != 0: return []
        return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]

    def launch(self, package_name: str, *, allow_sudo: bool = False) -> None:
        if MOCK: return
        r = runner.run(["waydroid", "app", "launch", package_name], timeout_s=60, allow_sudo=allow_sudo, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)

    def remove(self, package_name: str, *, allow_sudo: bool = False) -> None:
        if MOCK: return
        r = runner.run(["waydroid", "app", "remove", package_name], timeout_s=120, allow_sudo=allow_sudo, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
