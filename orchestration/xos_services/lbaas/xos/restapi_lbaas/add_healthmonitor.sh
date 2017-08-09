#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "provider_service": 9,
    "name": "http",
    "type": "HTTP",
    "delay": 5,
    "max_retries": 5,
    "timeout": 5,
    "http_method": "GET",
    "admin_state_up": true,
    "url_path": "/",
    "expected_codes": "200"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/healthmonitors/
