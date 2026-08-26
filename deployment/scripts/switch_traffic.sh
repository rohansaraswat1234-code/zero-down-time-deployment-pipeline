#!/bin/bash

set -e

TARGET=$1
STATE_FILE="deployment/blue-green/active-environment.txt"
NGINX_CONFIG="deployment/blue-green/nginx.conf"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
    echo "Usage: $0 blue|green"
    exit 1
fi

if [ "$TARGET" = "blue" ]; then
    TARGET_PORT=5002
else
    TARGET_PORT=5003
fi

CURRENT=$(cat "$STATE_FILE" 2>/dev/null || echo "blue")

echo "Current environment: $CURRENT"
echo "Target environment: $TARGET"

echo "Checking $TARGET health..."

if ! curl -fsS "http://localhost:$TARGET_PORT/health" > /dev/null; then
    echo "ERROR: $TARGET is unhealthy."
    echo "Traffic remains on $CURRENT."
    exit 1
fi

echo "$TARGET is healthy."

cat > "$NGINX_CONFIG" <<EOF
upstream backend {
    server $TARGET:5000;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

echo "Testing Nginx configuration..."

docker exec zero-downtime-nginx nginx -t

echo "Switching traffic to $TARGET..."

docker exec zero-downtime-nginx nginx -s reload

sleep 2

if curl -fsS "http://localhost:8080/health" > /dev/null; then
    echo "$TARGET" > "$STATE_FILE"
    echo "SUCCESS: Traffic switched to $TARGET without downtime."
else
    echo "ERROR: New deployment failed after traffic switch."
    echo "Rolling back to $CURRENT..."

    cat > "$NGINX_CONFIG" <<EOF
upstream backend {
    server $CURRENT:5000;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

    docker exec zero-downtime-nginx nginx -s reload

    echo "ROLLBACK COMPLETE: Traffic restored to $CURRENT."
    exit 1
fi