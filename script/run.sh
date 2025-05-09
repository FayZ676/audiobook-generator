#!/bin/bash

if [ ! -f .env.local ]; then
    echo "Error: .env.local file not found!"
    exit 1
fi

set -a
source .env.local
set +a

python tta_script/rp_handler.py --rp_serve_api --rp_api_port 8001