#!/usr/bin/env bash
# AIM Overlay — create isolated venv and install deps
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"

echo "-> Creating virtual environment in $VENV"
python3 -m venv "$VENV"

echo "-> Installing PyQt6..."
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install PyQt6 -q

echo ""
echo "Done. Run: ./run.sh"
