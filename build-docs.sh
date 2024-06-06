#!/bin/bash
# This script is used to build the documentation (for the vercel hosted website)
# Thus I didn't bother setting up stuff like venv here ;)

# The "python3 -m" prefixes are required to properly work on my Mac

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Bundle/transpile the JavaScript file(s). This is similar to `build.sh`
cd typescript/
npm install
npm run build
cd ..

# Copy the JavaScript build output to the expected locations
[[ ! -d src/mkdocs_placeholder_plugin/assets/ ]] && mkdir src/mkdocs_placeholder_plugin/assets/
# Files for use by the plugin
cp typescript/build/placeholder.min.js* src/mkdocs_placeholder_plugin/assets/
# Files for download
cp typescript/build/placeholder.min.js* public/

# install the dependencies
python3 -m pip install -r requirements.txt
# also install the latest (dev) version of this package
python3 -m pip install .

# Vercel prefers outputs to be in public/
python3 -m mkdocs build -d public

build_with_theme() {
    python3 -m mkdocs build -t "$1" -d public/"$1"
}

# Build with other themes
build_with_theme mkdocs
build_with_theme readthedocs
