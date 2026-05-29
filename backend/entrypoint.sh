#!/usr/bin/env bash
set -euo pipefail

export DISPLAY="${DISPLAY:-:99}"

Xvfb "$DISPLAY" -screen 0 1440x900x24 -ac +extension RANDR &
fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display "$DISPLAY" -forever -shared -nopw -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
/usr/share/novnc/utils/novnc_proxy --listen 6080 --vnc localhost:5900 >/tmp/novnc.log 2>&1 &

exec uvicorn main:app --host 0.0.0.0 --port 8000