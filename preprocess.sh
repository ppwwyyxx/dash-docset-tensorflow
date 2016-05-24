#!/bin/bash -e
# File: preprocess.sh
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

which parallel > /dev/null 2>&1 && {
	find "$1" -type f -name '*.html' | parallel ./transform.py '{}'
} || {
	find "$1" -type f -name '*.html' -exec ./transform.py {} \;
}
