#!/bin/bash -e
# File: preprocess.sh
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

rm "$1"/versions/master -rf
find "$1" -type f -name '*.html' -exec ./transform.py {} \;
