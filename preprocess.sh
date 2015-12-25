#!/bin/bash -e
# File: preprocess.sh
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

find "$1" -type f -name '*.html' -exec ./transform.py {} \;
