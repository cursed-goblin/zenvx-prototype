from __future__ import annotations

import shutil
from typing import List

from .utils import CheckResult, MOCK


def _has(cmd: str) -> bool:
    if MOCK: return True
    return shutil.which(cmd) is not None


def run_doctor() -> List[CheckResult]:
    checks: List[CheckResult] = []
    checks.append(CheckResult("python", "PASS", "Python runtime OK"))

    checks.append(CheckResult("waydroid", "PASS" if _has("waydroid") else "WARN", "waydroid present" if _has("waydroid") else "waydroid missing", "sudo apt install waydroid" if not _has("waydroid") else None))
    checks.append(CheckResult("wine", "PASS" if _has("wine") else "WARN", "wine present" if _has("wine") else "wine missing", "sudo apt install wine winetricks" if not _has("wine") else None))
    checks.append(CheckResult("aapt", "PASS" if (_has("aapt2") or _has("aapt")) else "WARN", "APK metadata tools present" if (_has("aapt2") or _has("aapt")) else "aapt2/aapt missing", "sudo apt install aapt" if not (_has("aapt2") or _has("aapt")) else None))

    rpm_ok = all(_has(x) for x in ("rpm", "rpm2cpio", "cpio", "proot"))
    checks.append(CheckResult("rpm-tools", "PASS" if rpm_ok else "WARN", "rpm2cpio/cpio/proot present" if rpm_ok else "RPM compatibility tools missing", "sudo apt install rpm rpm2cpio cpio proot" if not rpm_ok else None))

    return checks
