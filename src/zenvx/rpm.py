from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .commands import runner
from .utils import RPM_ROOTS_DIR, slugify, MOCK


@dataclass
class RpmInstallResult:
    rootfs: Path
    candidates: List[str]
    mode: str


class RPMAdapter:
    runtime = "rpm"

    def is_ready(self) -> bool:
        if MOCK: return True
        for tool in ("rpm2cpio", "cpio", "proot", "rpm"):
            if runner.run(["which", tool], timeout_s=10).returncode != 0:
                return False
        return True

    def install(self, rpm_path: Path, display_name: str) -> RpmInstallResult:
        app_slug = slugify(display_name)
        root_dir = RPM_ROOTS_DIR / app_slug
        rootfs = root_dir / "rootfs"
        rootfs.mkdir(parents=True, exist_ok=True)

        if MOCK:
            return RpmInstallResult(rootfs=rootfs, candidates=["/usr/bin/mockapp"], mode="mock")

        cmd = ["bash", "-lc", f"rpm2cpio {json.dumps(str(rpm_path))} | (cd {json.dumps(str(rootfs))} && cpio -idmv)"]
        r = runner.run(cmd, timeout_s=600, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)

        candidates: List[str] = []
        bin_dir = rootfs / "usr/bin"
        if bin_dir.exists():
            for p in bin_dir.glob("*"):
                if p.is_file(): candidates.append("/usr/bin/" + p.name)
        return RpmInstallResult(rootfs=rootfs, candidates=candidates, mode="proot")

    def launch(self, rootfs: Path, target: str) -> None:
        if MOCK: return
        r = runner.run(["proot", "-r", str(rootfs), target], timeout_s=3600, runtime=self.runtime)
        if r.returncode != 0: raise RuntimeError(r.stderr or r.stdout)
