#!/usr/bin/env bash

set -Eeuo pipefail

initial_seconds=$SECONDS && echo "🚀 Starting CI..." && echo && echo

stage_initial_seconds=$SECONDS && echo "🏗 Running BUILD stage..." && echo

do_build="${1:-}"
if [[ -z "${do_build}" ]]; then
  make build
fi
make deps

echo && echo "🆗 BUILD stage took $((SECONDS - stage_initial_seconds)) seconds." && echo

stage_initial_seconds=$SECONDS && echo "🍄 Running PREPARE stage..." && echo

make prepare

echo && echo "🆗 PREPARE stage took $((SECONDS - stage_initial_seconds)) seconds." && echo

stage_initial_seconds=$SECONDS && echo "👯‍ Running PARALLEL stage..." && echo

make validate-docker-compose
make security-code-analysis
make static-code-analysis
make unit-tests
make integration-tests
make functional-tests

echo && echo "🆗 PARALLEL stage took $((SECONDS - stage_initial_seconds)) seconds." && echo

stage_initial_seconds=$SECONDS && echo "🗑 Running CLEAN stage..." && echo

make stop
do_clean="${1:-}"
if [[ -z "${do_clean}" ]]; then
  make clean
fi

echo && echo "🆗 CLEAN stage took $((SECONDS - stage_initial_seconds)) seconds." && echo

echo && echo "🌈 CI finished in $((SECONDS - initial_seconds)) seconds." && echo
