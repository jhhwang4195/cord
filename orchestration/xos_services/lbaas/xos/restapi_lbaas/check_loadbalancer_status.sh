#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: get_loadbalancer.sh <loadbalancer_id>"
    exit -1
fi

ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/tenant/loadbalancers/$ID/check/
