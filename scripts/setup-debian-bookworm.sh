#!/usr/bin/env bash
set -euo pipefail

if [[ -f /etc/os-release ]]; then
	. /etc/os-release
else
	echo "[FAIL] /etc/os-release not found."
	exit 1
fi

if [[ "${ID:-}" != "debian" || "${VERSION_CODENAME:-}" != "bookworm" ]]; then
	echo "[WARN] Target is Debian 12 (bookworm). Detected ID=${ID:-} VERSION_CODENAME=${VERSION_CODENAME:-}"
fi

echo "This script can install ZenvX dependencies via apt."
echo "It will NOT run apt automatically without confirmation."

read -r -p "Run 'sudo apt update' first? [y/N] " DO_UPDATE
if [[ "${DO_UPDATE}" == "y" || "${DO_UPDATE}" == "Y" ]]; then
	sudo apt update
fi

read -r -p "Install base packages with apt? [y/N] " DO_INSTALL
if [[ "${DO_INSTALL}" == "y" || "${DO_INSTALL}" == "Y" ]]; then
	sudo apt install -y \
		python3 python3-venv python3-pip sqlite3 desktop-file-utils xdg-utils file findutils grep sed awk \
		rpm rpm2cpio cpio proot \
		wine winetricks \
		waydroid \
		libfuse2
else
	echo "[INFO] Skipping apt install."
fi
