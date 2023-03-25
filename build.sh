#!/usr/bin/env bash

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

# On MacOS the podman VM needs to be started first
if [[ "$(uname)" == "Darwin" ]]; then
    podman machine start
fi

# Build Typescript code
podman run -it --rm -v "$(pwd)/typescript:/mnt" localhost/placeholder-npm:latest
cp typescript/build/bundle.min.js src/mkdocs_placeholder_plugin/javascript/70_typescript_output.js

# Build python plugin
pip install .

# Start the web server
mkdocs serve
