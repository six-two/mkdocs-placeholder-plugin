#!/usr/bin/env bash

is_installed() {
    command -v "$1" &>/dev/null
}

PODMAN=""
if is_installed podman; then
    PODMAN=podman
elif is_installed docker; then
    PODMAN=docker # podman and docker are mostly compatible
else
    echo "[-] You seem to be missing container software (docker or podman). JS minification will not work"
fi

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

# On MacOS the podman VM needs to be started first
# if [[ "$(uname)" == "Darwin" ]]; then
#     podman machine start
# fi

# Build Typescript code
if [[ -n "$PODMAN" ]]; then
    echo "[*] Building minified JavaScript code"
    if ! $PODMAN run -it --rm -v "$(pwd)/typescript:/mnt" localhost/placeholder-npm:latest; then
        echo "[-] $PODMAN container not found, trying to build it. This may take a while if it needs to download the base images"
        if $PODMAN build --tag placeholder-npm typescript/; then
            echo "[*] Trying to run the $PODMAN container again"
            $PODMAN run -it --rm -v "$(pwd)/typescript:/mnt" localhost/placeholder-npm:latest
        else
            echo "[!] Failed to build $PODMAN container"
        fi
    fi
fi

# Copy output files
[[ ! -d src/mkdocs_placeholder_plugin/assets/ ]] && mkdir src/mkdocs_placeholder_plugin/assets/
cp typescript/build/placeholder.min.js* src/mkdocs_placeholder_plugin/assets/


# Build python plugin
# Use a virtual environment to not mess with system packages
if [[ ! -f venv/bin/activate ]]; then
    echo "[*] Creating virtual python environment"
    python -m venv --clear --upgrade-deps ./venv
fi

echo "[*] Installing python packages"
source venv/bin/activate
pip install -r requirements.txt
pip install .

echo "[*] Starting web server"
mkdocs serve "$@"
