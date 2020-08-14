#!/usr/bin/env bash

set -Eeuo pipefail

echo -ne "Waiting for RabbitMQ..."
while ! curl -sf "http://${RABBITMQ_HOST}:${RABBITMQ_UI_PORT}" &> /dev/null; do
    echo -ne "."
    sleep 1
done
echo -ne " ready!\n"
