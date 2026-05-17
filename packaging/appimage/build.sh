#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/appimage"
DIST_DIR="$PROJECT_ROOT/dist"
PY_VERSION="${PY_VERSION:-3.11}"
APP_NAME="linux-overlay-sight"

cd "$PROJECT_ROOT"

rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

python3 -m venv "$BUILD_DIR/venv"
VENV="$BUILD_DIR/venv/bin"
"$VENV/pip" install --upgrade --quiet pip wheel build hatchling python-appimage

"$VENV/python" -m build --wheel --outdir "$BUILD_DIR/wheel"
WHEEL="$(ls "$BUILD_DIR/wheel/"*.whl | head -n1)"
[[ -f "$WHEEL" ]] || { echo "wheel build failed"; exit 1; }

RECIPE="$BUILD_DIR/$APP_NAME"
mkdir -p "$RECIPE"

cp "$PROJECT_ROOT/packaging/appimage/entrypoint.sh"      "$RECIPE/entrypoint.sh"
cp "$PROJECT_ROOT/packaging/linux-overlay-sight.desktop" "$RECIPE/$APP_NAME.desktop"
cp "$PROJECT_ROOT/assets/linux-overlay-sight-256.png"    "$RECIPE/$APP_NAME.png"

sed -i "s/^Name=.*/Name=$APP_NAME/" "$RECIPE/$APP_NAME.desktop"

echo "$WHEEL" > "$RECIPE/requirements.txt"

cd "$BUILD_DIR"
"$VENV/python-appimage" build app -p "$PY_VERSION" "$RECIPE"

OUTPUT="$(find "$BUILD_DIR" -maxdepth 1 -name '*.AppImage' -print -quit)"
[[ -n "$OUTPUT" && -f "$OUTPUT" ]] || { echo "AppImage not produced"; exit 1; }

PROJ_VERSION="$(grep -oP '(?<=^version = ")[^"]+' "$PROJECT_ROOT/pyproject.toml")"
ARCH="$(uname -m)"
FINAL="$DIST_DIR/${APP_NAME}-${PROJ_VERSION}-${ARCH}.AppImage"
mv "$OUTPUT" "$FINAL"
chmod +x "$FINAL"

echo "✓ $FINAL ($(du -h "$FINAL" | cut -f1))"
