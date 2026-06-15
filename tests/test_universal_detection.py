from pathlib import Path

from zenvx.universal import detect_file


def test_detect_by_extension(tmp_path: Path) -> None:
    p = tmp_path / 'a.apk'; p.write_bytes(b'x'); assert detect_file(p).kind == 'apk'
    p = tmp_path / 'b.exe'; p.write_bytes(b'MZ' + b'0'*10); assert detect_file(p).kind == 'exe'
    p = tmp_path / 'c.rpm'; p.write_bytes(b'x'); assert detect_file(p).kind == 'rpm'
    p = tmp_path / 'd.AppImage'; p.write_bytes(b'\x7fELFAppImage'); assert detect_file(p).kind == 'appimage'
