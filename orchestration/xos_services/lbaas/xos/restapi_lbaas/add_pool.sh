#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: add_pool.sh <health_monitor_id>"
    exit -1
fi

HEALTH_ID=$1

DATA=$(cat <<EOF
{
    "provider_service": 9,
    "name": "sona_pool",
    "subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
    "health_monitor_id": "$HEALTH_ID",
    "lb_algorithm": "ROUND_ROBIN",
    "protocol": "HTTP",
    "description": "sona_pool"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/
