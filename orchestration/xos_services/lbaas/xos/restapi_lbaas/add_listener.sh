#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "provider_service": 9,
    "name": "sona_listener",
    "protocol": "HTTP",
    "protocol_port": 1001,
    "stat_port": 10002,
    "description": "sona_listener"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/listeners/
