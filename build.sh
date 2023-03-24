#!/usr/bin/env bash

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

cd typescript
podman run -it --rm -v "$(pwd):/mnt" localhost/placeholder-npm:latest
cp bin/bundle.min.js ../src/mkdocs_placeholder_plugin/javascript/70_typescript_output.js

cd ..
pip install .
mkdocs serve
