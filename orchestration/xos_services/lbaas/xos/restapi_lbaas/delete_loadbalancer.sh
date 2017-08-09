#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: delete_loadbalancer.sh <loadbalancer_id>"
    exit -1
fi

LB_ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/loadbalancers/$LB_ID/ -v
