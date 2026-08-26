#!/bin/bash

set -e

STATE_FILE="deployment/blue-green/active-environment.txt"
HISTORY_FILE="data/deployments.csv"

CURRENT=$(cat "$STATE_FILE" 2>/dev/null || echo "blue")

if [ "$CURRENT" = "blue" ]; then
    TARGET="green"
else
    TARGET="blue"
fi

echo "Current environment: $CURRENT"
echo "Deploying new version to: $TARGET"

docker compose -f deployment/blue-green/docker-compose.yml build "$TARGET"

docker compose -f deployment/blue-green/docker-compose.yml up -d "$TARGET"

echo "Waiting for application to start..."
sleep 5

if ./deployment/scripts/switch_traffic.sh "$TARGET"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S'),$CURRENT,$TARGET,SUCCESS" >> "$HISTORY_FILE"

    echo "Deployment completed successfully."
    echo "Active environment: $TARGET"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S'),$CURRENT,$TARGET,FAILED" >> "$HISTORY_FILE"

    echo "Deployment failed."
    echo "Traffic remains on: $CURRENT"
    exit 1
fi