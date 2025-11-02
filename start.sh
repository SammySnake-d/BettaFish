#!/bin/bash

# 快速启动脚本

if [ -d "venv" ]; then
    source venv/bin/activate
    python app.py
else
    python3 app.py
fi
