#!/bin/bash

# 快速启动脚本

if [ -d "venv" ]; then
    source venv/bin/activate
    gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --preload wsgi:app
else
    python3 -m gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --preload wsgi:app
fi
