#!/usr/bin/env bash

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

# On MacOS the podman VM needs to be started first
if [[ "$(uname)" == "Darwin" ]]; then
    podman machine start
fi

# Build Typescript code
podman run -it --rm -v "$(pwd)/typescript:/mnt" localhost/placeholder-npm:latest
# Copy output files
[[ ! -d src/mkdocs_placeholder_plugin/assets/ ]] && mkdir src/mkdocs_placeholder_plugin/assets/
cp typescript/build/placeholder.min.js* src/mkdocs_placeholder_plugin/assets/


# Build python plugin
pip install .

# Start the web server
mkdocs serve
