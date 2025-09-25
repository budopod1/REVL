#!/usr/bin/env bash

free_port() {
    lsof -iTCP:7775 -sTCP:LISTEN | tail -1 | awk '{print $2}' | xargs -r kill
}
free_port
trap "free_port" SIGINT SIGTERM

python driver.py &
cd html
python -m http.server
