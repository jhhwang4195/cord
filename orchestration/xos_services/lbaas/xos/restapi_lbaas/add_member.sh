#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: add_member.sh <pool_id> <member_ip>"
    exit -1
fi

POOL_ID=$1
MEMBER_IP=$2

DATA=$(cat <<EOF
{
    "provider_service": 9,
    "memberpool": "$POOL_ID",
    "address": "$MEMBER_IP",
    "protocol_port": 80,
    "subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/members/
