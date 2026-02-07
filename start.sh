#!/bin/bash
if [ ! -d "venv" ]; then
    python3 -m venv venv
    venv/bin/pip install -r requirements.txt
    venv/bin/pip install flask
fi
# Start Admin Panel in background
nohup venv/bin/python admin_server.py > admin.log 2>&1 &
echo "Admin Panel started on port 5000"

# Start Bot
venv/bin/python bot.py
