# ZenvX ISO build (GitHub Actions)

This folder contains a minimal **Debian Bookworm live ISO** build recipe using `live-build`.

## Output
- ISO artifact is uploaded by GitHub Actions as `zenvx-bookworm-xfce-iso`.

## What’s inside the ISO
- Debian Bookworm live system
- XFCE desktop
- ZenvX prototype source at `/opt/zenvx`
- Desktop launcher: **ZenvX (Prototype)**

## How it works
The workflow runs `iso/build.sh`, which:
- configures `live-build`
- adds an APT package list (XFCE + basics)
- copies this repo into the chroot as `/opt/zenvx`
- installs a `.desktop` file launching ZenvX in mock mode

## Local build (optional)
On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y live-build
bash iso/build.sh
```

The ISO will be under `iso/out/`.
