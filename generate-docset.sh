#!/bin/bash -e
cd "$(dirname "$0")"

rm -rf ./html || true
cp -r "$1" ./html/

./transform.py ./html

find html -name '*.md' -delete
find html -name '*.html' -type f \
  -exec sed -i -E 's/href="([^"]+)\.md(["#])/href="\1.html\2/g' '{}' \;

cp -i -v style.css icon*.png dashing.json html/

pushd html
dashing build
popd

cp -v meta.json "html/TensorFlow 2.docset/"
