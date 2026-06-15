from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Detected:
    kind: str
    reason: str


def detect_file(path: Path) -> Detected:
    lower = path.name.lower()
    if lower.endswith(".apk"): return Detected("apk", "extension")
    if lower.endswith(".exe") or lower.endswith(".msi"): return Detected("exe", "extension")
    if lower.endswith(".rpm"): return Detected("rpm", "extension")
    if lower.endswith(".appimage"): return Detected("appimage", "extension")

    try:
        head = path.read_bytes()[:4096]
        if head.startswith(b"MZ"): return Detected("exe", "magic:MZ")
        if head.startswith(b"\x7fELF") and b"AppImage" in head: return Detected("appimage", "magic:ELF+AppImage")
    except Exception:
        pass
    return Detected("unknown", "unrecognized")
