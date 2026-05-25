#!/usr/bin/env bash
# switch to this script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )"

rm -r docs.bak
cp -r docs docs.bak

markdown-placeholder-standalone --docs docs.bak/ --placeholder-extra-js placeholder-extra.js --phase markdown
mkdocs build -f mkdocs-standalone-test.yml
markdown-placeholder-standalone --docs site/ --placeholder-extra-js placeholder-extra.js --phase html

python3 -m http.server --directory site/
