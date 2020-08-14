#!/usr/bin/env bash

set -Eeuo pipefail

echo -ne "Waiting for MongoDB..."
while ! nc -z ${MONGODB_HOST} ${MONGODB_PORT} &> /dev/null; do
  echo -ne "."
  sleep 1
done
echo -ne " ready!\n"
