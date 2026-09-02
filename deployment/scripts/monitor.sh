#!/bin/bash

STATE_FILE="deployment/blue-green/active-environment.txt"
HISTORY_FILE="data/deployments.csv"

CURRENT=$(cat "$STATE_FILE")

if [ "$CURRENT" = "blue" ]; then
    CURRENT_PORT=5002
    FALLBACK="green"
else
    CURRENT_PORT=5003
    FALLBACK="blue"
fi

echo "Monitoring active environment: $CURRENT"

if curl -fsS "http://localhost:$CURRENT_PORT/health" > /dev/null; then
    echo "$CURRENT is healthy."
else
    echo "$CURRENT is unhealthy!"
    echo "Starting automatic rollback to $FALLBACK..."

    ./deployment/scripts/switch_traffic.sh "$FALLBACK"

    echo "$(date '+%Y-%m-%d %H:%M:%S'),$CURRENT,$FALLBACK,ROLLBACK" >> "$HISTORY_FILE"

    echo "Automatic rollback completed."
fi
