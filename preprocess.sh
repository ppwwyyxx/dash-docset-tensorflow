#!/bin/zsh -e
# File: preprocess.sh
# Author: Yuxin Wu

[[ -z "$1" ]] && exit 1

[[ -f "$1/main.css" ]] || {
	echo "Need to copy main.css first! See README."
  exit 1
}

set +e
# contains a lot of case-insensitive duplicate file names which is not allowed by dash-user-contrib
rm -rf "$1"/versions/*/api_docs/python/tf/contrib/keras*
rm -rf "$1"/versions/*/api_docs/java
set -e


which parallel > /dev/null 2>&1 && {
	find "$1" -type f -name '*.html' | parallel --eta ./transform.py '{}'
} || {
	find "$1" -type f -name '*.html' -exec ./transform.py {} \;
}

find "$1" -type f -name "*.mp4" -delete

# rename case-insensitive duplicates
for i in $(find www.tensorflow.org/ | sort -f | uniq -di); do
	dn=$(dirname $i)
	fn=$(basename $i)
	mv -v $i $dn/dedup_$fn
done
