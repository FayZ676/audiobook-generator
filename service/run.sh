#!/bin/bash

if [ ! -f .env.local ]; then
    echo "Error: .env.local file not found!"
    exit 1
fi

set -a
source .env.local
set +a

uvicorn tta_service.main:app --reload --port 8000