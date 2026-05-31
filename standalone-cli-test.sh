#!/usr/bin/env bash
# switch to this script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )"

if [[ $# -eq 1 ]] && [[ "$1" == both || "$1" == split ]]; then
    MODE="$1"
else
    echo "[!] Usage: <MODE>"
    echo "Where MODE can be one of:"
    echo "- 'both': replace placeholders in one call"
    echo "- 'split': separate invocations during markdown and html phase"
    exit 1
fi

rm -r docs.bak
cp -r docs docs.bak

if [[ "$MODE" == split ]]; then
    markdown-placeholder-standalone docs.bak/ --placeholder-extra-js placeholder-extra.js --phase markdown
    properdocs build -f properdocs-standalone-test.yml
    markdown-placeholder-standalone site/ --placeholder-extra-js placeholder-extra.js --phase html
else
    properdocs build -f properdocs-standalone-test.yml
    markdown-placeholder-standalone site/ --placeholder-extra-js placeholder-extra.js --phase both
fi

python3 -m http.server --directory site/
