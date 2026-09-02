#!/bin/bash

CURRENT=$(cat deployment/blue-green/active-environment.txt)

if [ "$CURRENT" = "green" ]; then
    TARGET="blue"
else
    TARGET="green"
fi

echo "Current environment: $CURRENT"
echo "Rollback target: $TARGET"

./deployment/scripts/switch_traffic.sh "$TARGET"

echo "Rollback completed."