#!/bin/bash

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - INFO - Waiting for ${RABBIT_HOST}:${RABBIT_PORT}"
    sleep 3
done

# Run Service
nameko run --config config.yml hunk.service
