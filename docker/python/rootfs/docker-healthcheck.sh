#!/usr/bin/env bash

set -Eeuo pipefail

/mongodb-healthcheck.sh
/rabbitmq-healthcheck.sh
