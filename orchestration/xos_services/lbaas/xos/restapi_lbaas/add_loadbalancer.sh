#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: add_loadbalancer.sh <listener_id> <pool_id>"
    exit -1
fi

LISTENER_ID=$1
POOL_ID=$2

DATA=$(cat <<EOF
{
    "owner": 1,
    "name": "sona_loadbalancer",
    "listener": "$LISTENER_ID",
    "pool": "$POOL_ID",
    "vip_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
    "vip_address": "0.0.0.0",
    "description": "web server loadbalancer"
}
EOF
)

<< "COMMENT"
DATA=$(cat <<EOF
{
    "owner": 1,
    "name": "sona_loadbalancer",
    "vip_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
    "vip_address": "10.6.1.198",
    "description": "web server loadbalancer100"
}
EOF
)
COMMENT

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/loadbalancers/
