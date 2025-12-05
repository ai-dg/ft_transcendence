#!/bin/bash

set -a
source ./srcs/.env
set +a

KIBANA_URL="http://localhost:$PORT_KIBANA"
KIBANA_USER="$ELASTIC_USERNAME"
KIBANA_PASSWORD="$ELASTIC_PASSWORD"

echo "⏳ Waiting for Kibana to be ready on port $PORT_KIBANA..."

timeout=120
elapsed=0

while true; do
	STATUS_RESPONSE=$(curl -u "$KIBANA_USER:$KIBANA_PASSWORD" -s "$KIBANA_URL/api/status")
	STATE=$(echo "$STATUS_RESPONSE" | jq -r '.status.overall.state' 2>/dev/null)

	if [ "$STATE" == "green" ]; then
		echo "✅ Kibana is ready"
		break
	fi

	sleep 5
	elapsed=$((elapsed + 5))
	if [ "$elapsed" -ge "$timeout" ]; then
		echo "❌ Kibana is not ready after $timeout seconds."
		exit 1
	fi
done
