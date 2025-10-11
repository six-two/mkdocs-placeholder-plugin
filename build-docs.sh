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

is_installed() {
    command -v "$1" &>/dev/null
}

poetryw() {
    if is_installed poetry; then
        poetry "$@"
    else
        python3 -m poetry "$@"
    fi
}

# Build everything with vercel
# Vercel installs python scripts in weird directories like /python312/bin that are not in the PATH
export PATH="$PATH:$(python3 -m site --user-base)/bin"
poetryw install
poetryw run mkdocs build -d public

# Files for download
cp typescript/build/placeholder.min.js* public/

build_with_theme() {
    poetryw run mkdocs build -t "$1" -d public/"$1"
}

# Build with other themes
build_with_theme mkdocs
build_with_theme readthedocs
