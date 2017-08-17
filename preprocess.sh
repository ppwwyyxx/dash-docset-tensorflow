#!/bin/zsh -e
# File: preprocess.sh
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

[[ -z "$1" ]] && exit 1

which parallel > /dev/null 2>&1 && {
	find "$1" -type f -name '*.html' | parallel --eta ./transform.py '{}'
} || {
	find "$1" -type f -name '*.html' -exec ./transform.py {} \;
}

set +e
rm -rf "$1"/versions/master/api_docs/python/tf/contrib/keras
set -e

find "$1" -type f -name "*.mp4" -delete
