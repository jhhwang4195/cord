#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: delete_listener.sh <listener_id>"
    exit -1
fi

LISTENER_ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/listeners/$LISTENER_ID/ -v
