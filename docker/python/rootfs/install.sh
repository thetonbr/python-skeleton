#!/usr/bin/env bash

set -Eeuo pipefail

root_path=${1:-/app}

pip install -q -r "$root_path/src/requirements.txt"
