#!/usr/bin/env bash
lsof -iTCP:7775 -sTCP:LISTEN | tail -1 | awk '{print $2}' | xargs -r kill
python driver.py &
cd html
python -m http.server
