#!/usr/bin/env bash

set -Eeuo pipefail

root_path=${1:-/app}

pip3 install -q -r "$root_path/src/requirements.txt"
pip3 install -q -r "$root_path/tests/requirements.txt"

lock "$root_path/src/requirements.txt"
lock "$root_path/tests/requirements.txt"

sort-requirements "$root_path/src/requirements.txt"
sort-requirements "$root_path/tests/requirements.txt"
