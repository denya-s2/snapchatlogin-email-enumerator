#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo_info()    { echo -e "${GREEN}[SNAPENUM.INFO.LINSETUP]${NC} $1"; }
echo_warn()    { echo -e "${YELLOW}[SNAPENUM.WARNING.LINSETUP]${NC} $1"; }
echo_error()   { echo -e "${RED}[SNAPENUM.ERROR.LINSETUP]${NC} $1"; }

echo_info "Checking for Python3..."

if ! command -v python3 &>/dev/null; then
    echo_error "Python3 is not installed or not in PATH. Please install Python3.12+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

echo_info "Found Python3 version: $PYTHON_VERSION"

if [[ "$PYTHON_MAJOR" -lt 3 ]] || { [[ "$PYTHON_MAJOR" -eq 3 ]] && [[ "$PYTHON_MINOR" -lt 12 ]]; }; then
    echo_warn "Python3 version $PYTHON_VERSION is below 3.12. Some features may not work correctly."
fi

CHROME_DIR="./chrome-linux64-146.0.7680.165"
CHROME_XZ_BINARY="chrome.xz"
CHROME_BINARIES=(
    "chrome"
    "chrome-wrapper"
    "chrome_sandbox"
    "chrome_crashpad_handler"
)

echo_info "Setting executable permissions in '$CHROME_DIR'..."

if [[ ! -d "$CHROME_DIR" ]]; then
    echo_error "Chrome directory '$CHROME_DIR' not found in $(pwd)"
    exit 1
fi

FULL_CHROME_XZ_PATH=$CHROME_DIR/$CHROME_XZ_BINARY
if [[ ! -f "$FULL_CHROME_XZ_PATH" ]]; then
    echo_error "Archive not found: $FULL_CHROME_XZ_PATH"
    exit 1
fi
echo_info "Unpacking '$FULL_CHROME_XZ_PATH'"
unxz "$FULL_CHROME_XZ_PATH" --keep

for binary in "${CHROME_BINARIES[@]}"; do
    BINARY_PATH="$CHROME_DIR/$binary"
    if [[ ! -f "$BINARY_PATH" ]]; then
        echo_warn "Binary not found, skipping: $BINARY_PATH"
        continue
    fi
    if chmod +x "$BINARY_PATH"; then
        echo_info "chmod +x: $BINARY_PATH"
    else
        echo_error "Failed to chmod +x: $BINARY_PATH"
        exit 1
    fi
done

echo_info "All done!"
