#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: get_pool.sh <pool_id>"
    exit -1
fi

POOL_ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/tenant/pools/$POOL_ID/
