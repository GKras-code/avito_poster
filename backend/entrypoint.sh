#!/usr/bin/env bash
set -euo pipefail

export DISPLAY="${DISPLAY:-:99}"

wait_for_tcp_port() {
	local host="$1"
	local port="$2"
	local label="$3"

	for _ in $(seq 1 20); do
		if bash -lc "</dev/tcp/${host}/${port}" >/dev/null 2>&1; then
			return 0
		fi
		sleep 0.5
	done

	printf '%s did not start on %s:%s\n' "$label" "$host" "$port" >&2
	return 1
}

dump_vnc_logs() {
	for log_file in /tmp/fluxbox.log /tmp/x11vnc.log /tmp/novnc.log; do
		if [ -f "$log_file" ]; then
			printf '\n===== %s =====\n' "$log_file" >&2
			cat "$log_file" >&2
		fi
	done
}

Xvfb "$DISPLAY" -screen 0 1440x900x24 -ac +extension RANDR &

for _ in $(seq 1 20); do
	if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
		break
	fi
	sleep 0.5
done

fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display "$DISPLAY" -forever -shared -nopw -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
websockify --web /usr/share/novnc/ 6080 localhost:5900 >/tmp/novnc.log 2>&1 &

if ! wait_for_tcp_port localhost 5900 x11vnc; then
	dump_vnc_logs
	exit 1
fi

if ! wait_for_tcp_port localhost 6080 websockify; then
	dump_vnc_logs
	exit 1
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000