#!/usr/bin/env bash
# Build linux-overlay-sight-x86_64.AppImage from the current source tree.
#
# Strategy: python-appimage (https://github.com/niess/python-appimage) — bundles
# a relocatable manylinux Python plus our wheel and PyQt6 into a single AppImage
# that runs on any glibc >= 2.17 distro.
#
# Output: dist/linux-overlay-sight-1.0.0-cp311-cp311-manylinux2014_x86_64.AppImage
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/appimage"
DIST_DIR="$PROJECT_ROOT/dist"
PY_VERSION="${PY_VERSION:-3.11}"
APP_NAME="linux-overlay-sight"

cd "$PROJECT_ROOT"

echo "→ Cleaning previous build"
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

echo "→ Setting up isolated build venv"
python3 -m venv "$BUILD_DIR/venv"
VENV="$BUILD_DIR/venv/bin"
"$VENV/pip" install --upgrade --quiet pip wheel build hatchling python-appimage

echo "→ Building project wheel"
"$VENV/python" -m build --wheel --outdir "$BUILD_DIR/wheel"
WHEEL="$(ls "$BUILD_DIR/wheel/"*.whl | head -n1)"
[[ -f "$WHEEL" ]] || { echo "wheel build failed"; exit 1; }
echo "  wheel: $WHEEL"

echo "→ Preparing python-appimage recipe"
RECIPE="$BUILD_DIR/$APP_NAME"
mkdir -p "$RECIPE"

# Recipe files. python-appimage uses the directory name as app name.
cp "$PROJECT_ROOT/packaging/appimage/entrypoint.sh"   "$RECIPE/entrypoint.sh"
cp "$PROJECT_ROOT/packaging/linux-overlay-sight.desktop" \
   "$RECIPE/$APP_NAME.desktop"
cp "$PROJECT_ROOT/assets/linux-overlay-sight-256.png" \
   "$RECIPE/$APP_NAME.png"

# appimagetool turns Name= into the output filename and replaces spaces
# with underscores. python-appimage then looks for the original (spaced)
# name and crashes. Patch Name= to a no-space slug for the recipe copy
# only — the .desktop installed by AUR keeps its pretty "Linux Overlay
# Sight" name.
sed -i "s/^Name=.*/Name=$APP_NAME/" "$RECIPE/$APP_NAME.desktop"

# requirements.txt — install our wheel into the AppImage.
echo "$WHEEL" > "$RECIPE/requirements.txt"

echo "→ Building AppImage (python-appimage, py${PY_VERSION})"
cd "$BUILD_DIR"
"$VENV/python-appimage" build app -p "$PY_VERSION" "$RECIPE"

# python-appimage drops the AppImage in CWD. Be forgiving about the exact
# filename — appimagetool's naming has changed across releases.
OUTPUT="$(find "$BUILD_DIR" -maxdepth 1 -name '*.AppImage' -print -quit)"
[[ -n "$OUTPUT" && -f "$OUTPUT" ]] || { echo "AppImage not produced"; exit 1; }

PROJ_VERSION="$(grep -oP '(?<=^version = ")[^"]+' "$PROJECT_ROOT/pyproject.toml")"
ARCH="$(uname -m)"
FINAL="$DIST_DIR/${APP_NAME}-${PROJ_VERSION}-${ARCH}.AppImage"
mv "$OUTPUT" "$FINAL"
chmod +x "$FINAL"

echo ""
echo "✓ Done: $FINAL"
echo "  Size: $(du -h "$FINAL" | cut -f1)"
echo ""
echo "Run it: $FINAL"
