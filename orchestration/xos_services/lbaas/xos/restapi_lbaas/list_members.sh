#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: list_members.sh <pool_id>"
    exit -1
fi

ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/tenant/pools/$ID/members/
