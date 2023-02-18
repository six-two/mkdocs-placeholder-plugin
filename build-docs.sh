#!/bin/bash
# This script is used to build the documentation (for the vercel hosted website)
# Thus I didn't bother setting up stuff like venv here ;)

# The "python3 -m" prefixes are required to properly work on my Mac

# Switch to the directory of this file
cd "$( dirname "${BASH_SOURCE[0]}" )"

# install the dependencies
python3 -m pip install -r requirements.txt
# also install the latest (dev) version of this package
python3 -m pip install .

# Vercel prefers outputs to be in public/
python3 -m mkdocs build -d public

# Build with other themes
python3 -m mkdocs build -t mkdocs -d public/mkdocs
python3 -m mkdocs build -t readthedocs -d public/readthedocs
