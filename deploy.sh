#!/bin/bash
# Deployment script for mediautil (Option D: Manual deployment)
# Run this as the current user. No root required for installation to /opt.
# To complete installation, run the printed command as root.

set -euo pipefail

# Configuration
INSTALL_DIR="/opt/mediautil"
BIN_DIR="/usr/local/bin"
WRAPPER_NAME="mediautil"
WRAPPER_SOURCE="mediautil-wrapper.sh"

# Step 0: Verify dependencies
function check_dependency {
    local name="$1"
    local command="$2"
    local min_version="${3:-}"
    
    if ! command -v "$command" &>/dev/null; then
        echo "ERROR: Required dependency '$name' is not installed or not in PATH."
        echo "       Please install it before deploying."
        exit 1
    fi
    
    if [ -n "$min_version" ]; then
        local py_version major major_min minor minor_min
        major_min=${min_version%.*}
        minor_min=${min_version#*.}
        
        py_version=$("${command}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$(echo "$py_version" | cut -d. -f1)
        minor=$(echo "$py_version" | cut -d. -f2)
        
        if [ "$major" -lt "$major_min" ] || { [ "$major" -eq "$major_min" ] && [ "$minor" -lt "$minor_min" ]; }; then
            echo "ERROR: $name version $major.$minor is too old. Required: >= $major_min.$minor_min"
            exit 1
        fi
        echo "[OK] Found $name version $major.$minor ($(command -v "$command"))"
    else
        echo "[OK] Found $name ($(command -v "$command"))"
    fi
}

echo "Checking dependencies..."
check_dependency "Python" "python3" "3.7"
check_dependency "ffmpeg" "ffmpeg"
echo ""

# Step 1: Remove old installation if it exists
echo "Cleaning up old installation..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "[OK] Removed old installation from $INSTALL_DIR"
fi
echo ""

# Step 2: Create installation directory
mkdir -p "$INSTALL_DIR"

# Step 3: Copy project files, excluding tests and __pycache__
echo "Copying project files..."
# Copy the mediautil package directory
cp -r mediautil/ "$INSTALL_DIR/"
# Remove tests and __pycache__ from the installed directory
rm -rf "${INSTALL_DIR}/mediautil/tests"
find "${INSTALL_DIR}/mediautil" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "[OK] Copied files to $INSTALL_DIR/"

# Step 4: Copy wrapper source for reference
cp "$WRAPPER_SOURCE" "$INSTALL_DIR/"
echo "[OK] Wrapper script copied to $INSTALL_DIR/"
echo ""

# Step 5: Print instruction for root installation
echo "Deployment files installed to: $INSTALL_DIR/"
echo ""
echo "To complete installation, run the following as root:"
echo "  cp $INSTALL_DIR/$WRAPPER_SOURCE $BIN_DIR/$WRAPPER_NAME"
echo ""
echo "Then verify with: $WRAPPER_NAME --help"
