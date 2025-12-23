#!/usr/bin/env bash

# 1. Run Python Setup Script (Downloads everything reliably)
python setup_models.py

# 2. Start Server
uvicorn app:app --host 0.0.0.0 --port $PORT
