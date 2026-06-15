ZenvX Prototype (Debian Bookworm)

ZenvX is a **prototype compatibility-focused launcher** for Debian 12 (Bookworm) that provides a unified "Universal App" layer for:

- **Android APK** via **Waydroid** (prototype)
- **Windows EXE** via **Wine** (prototype)
- **Linux AppImage** via native AppImage runtime (prototype)
- **Linux RPM** via best-effort extraction + **proot** (experimental)

This project is **not a full operating system**. It does not replace the kernel, init system, bootloader, or desktop environment.

## Install (prototype)

```bash
cd ZenvX-Prototype
./scripts/setup-debian-bookworm.sh
./install.sh
```

## Run

```bash
./.venv/bin/python -m zenvx
./.venv/bin/python -m zenvx doctor
```

### Mock mode

```bash
ZENVX_MOCK=1 ./.venv/bin/python -m zenvx doctor
ZENVX_MOCK=1 ./.venv/bin/python -m zenvx install ./anything.exe
```

## Privacy
- No telemetry
- No network calls by default
- AI agent defaults to offline MockAgent
