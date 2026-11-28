#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=/project/bt_spp_acceptor

cd "$PROJECT_DIR"

echo "Building firmware..."
idf.py build

echo "Flashing firmware..."
cd "$PROJECT_DIR/build"
python -m esptool --chip esp32 -p "$ESPPORT" -b 460800 \
    --before default_reset --after hard_reset write_flash @flash_args

echo "Starting firmware monitor..."
cd "$PROJECT_DIR"
idf.py -p "$ESPPORT" monitor
