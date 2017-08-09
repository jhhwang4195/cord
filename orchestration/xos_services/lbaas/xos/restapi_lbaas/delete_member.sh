#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: delete_member.sh <pool_id> <member_id>"
    exit -1
fi

POOL_ID=$1
MEMBER_ID=$2

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/pools/$POOL_ID/members/$MEMBER_ID/ -v
