#!/usr/bin/env bash
# AIM Overlay — запуск
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"

if [[ ! -d "$VENV" ]]; then
    echo "Сначала запустите: ./setup.sh"
    exit 1
fi

exec "$VENV/bin/python" "$DIR/aim_overlay.py" "$@"
