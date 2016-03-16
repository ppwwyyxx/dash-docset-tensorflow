#!/bin/bash -e
# File: preprocess.sh
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

rm -rf $1/versions/r0.7/
find "$1" -type f -name '*.html' -exec ./transform.py {} \;
