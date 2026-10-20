#!/bin/bash
# One-click launcher for Club Activities Tracker on macOS

cd "$(dirname "$0")"

echo "============================================================"
echo " 🎯 Launching Club Activities Tracker..."
echo "============================================================"

# Open browser automatically after 1 second
(sleep 1 && open "http://localhost:8000") &

# Start python server
python3 app.py
