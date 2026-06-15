#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/iso/work"
OUT="$ROOT/iso/out"

mkdir -p "$WORK" "$OUT"

LOG="$OUT/build-$(date -u +%Y%m%dT%H%M%SZ).log"

{
  echo "[INFO] Starting ISO build";
  echo "[INFO] ROOT=$ROOT";
  echo "[INFO] WORK=$WORK";
  echo "[INFO] OUT=$OUT";

  rm -rf "$WORK/live"
  mkdir -p "$WORK/live"
  cd "$WORK/live"

  sudo lb config noauto \
    --mode debian \
    --distribution bookworm \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootappend-live "boot=live components quiet splash" \
    --iso-application "ZenvX Prototype" \
    --iso-publisher "ZenvX" \
    --iso-volume "ZenvX-Bookworm-XFCE" \
    --mirror-binary "http://deb.debian.org/debian/" \
    --mirror-chroot "http://deb.debian.org/debian/"

  sudo mkdir -p config/package-lists
  sudo cp "$ROOT/iso/package-lists/xfce.list.chroot" config/package-lists/

  # Force correct sources.list inside the chroot BEFORE lb_chroot_apt runs.
  # This prevents live-build from injecting the invalid 'bookworm/updates' security suite.
  sudo mkdir -p config/includes.chroot/etc/apt
  sudo install -m 0644 "$ROOT/iso/chroot-sources.list" config/includes.chroot/etc/apt/sources.list

  # Include the ZenvX repo in the live filesystem
  sudo mkdir -p config/includes.chroot/opt
  sudo rsync -a --delete \
    --exclude ".git" \
    --exclude "iso/work" \
    --exclude "iso/out" \
    "$ROOT/" "config/includes.chroot/opt/zenvx/"

  # Desktop entry
  sudo mkdir -p config/includes.chroot/usr/share/applications
  sudo cp "$ROOT/iso/zenvx-prototype.desktop" config/includes.chroot/usr/share/applications/zenvx-prototype.desktop

  sudo lb build 2>&1 | tee "$LOG"

  ls -la
  if ls *.iso >/dev/null 2>&1; then
    mv -v *.iso "$OUT/"
  else
    echo "[FAIL] No ISO produced";
    exit 1
  fi

  echo "[OK] ISO build finished";
}
