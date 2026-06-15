#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [[ -f /etc/os-release ]]; then
	. /etc/os-release
	if [[ "${ID:-}" != "debian" || "${VERSION_CODENAME:-}" != "bookworm" ]]; then
		echo "[WARN] Target is Debian 12 (bookworm). Detected: ID=${ID:-} VERSION_CODENAME=${VERSION_CODENAME:-}"
	fi
fi

mkdir -p "$HOME/.local/share/ZenvX/logs" "$HOME/.local/share/applications"

if [[ ! -d .venv ]]; then
	python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip || true

# NOTE: This repository is designed to be runnable offline.
# If you have network access you may optionally install extras.
if [[ -s requirements.txt ]]; then
	echo "[INFO] requirements.txt present. If you have network access, you can install it manually."
	echo "       Skipping pip install by default to avoid network dependency."
fi

install -m 0644 zenvx.desktop "$HOME/.local/share/applications/zenvx.desktop"
update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true

echo "[OK] Installed. Run: zenvx or ./.venv/bin/python -m zenvx"

cat <<'EOF'

Offline run examples:
  . .venv/bin/activate
  PYTHONPATH=./src python -m zenvx doctor
  PYTHONPATH=./src python -m zenvx gui

To install as a real 'zenvx' command (requires setuptools via pip):
  pip install -e .
EOF
