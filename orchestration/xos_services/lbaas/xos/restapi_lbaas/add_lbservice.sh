#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "service_name": "LBaaS"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/service/lbservices/
