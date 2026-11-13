#!/usr/bin/env bash
# Script launch Localhost Server on Linux / macOS
cd "$(dirname "$0")"
PORT="${1:-8000}"
echo "======================================================================"
echo "   STARTING NAM VIET AI AGENT LOCALHOST ON PORT ${PORT}"
echo "   Open browser: http://localhost:${PORT}"
echo "======================================================================"
python3 server.py "${PORT}"

