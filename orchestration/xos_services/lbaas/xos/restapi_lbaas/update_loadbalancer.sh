#!/bin/bash

source ./config.sh

if [[ "$#" -ne 3 ]]; then
    echo "Syntax: update_loadbalancer.sh <loadbalancer_id> <listener_id> <pool_id>"
    exit -1
fi

LB_ID=$1
LISTENER_ID=$2
POOL_ID=$3

DATA=$(cat <<EOF
{
    "listener_id": "$LISTENER_ID",
    "pool_id": "$POOL_ID"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/loadbalancers/$LB_ID/
