#!/usr/bin/env bash

# If something fails, exit immediately
set -e

# Switch into the script directory
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Reinstall the pacakage to make sure it is up to date
python3 -m pip install --user .

# Build the documentation
python3 -m mkdocs build

# Remove the placeholder JavaScript code
rm site/assets/javascripts/placeholder-plugin.js

# Try to replace the plcaeholders in all HTML files
mkdocs-placeholder-replace-static.py -p placeholder-plugin.yaml -b site "**/*.html"

# Serve the results, so that you can manually verify that it looks as expected
echo "[*] Starting webserver. Please check the test pages manually: http://127.0.0.1:8000/tests/basic/"
python3 -m http.server --directory site --bind 127.0.0.1
