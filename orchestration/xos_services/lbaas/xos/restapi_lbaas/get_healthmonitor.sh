#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: get_healthmonitor.sh <health_monitor_id>"
    exit -1
fi

HEALTH_ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/tenant/healthmonitors/$HEALTH_ID/
