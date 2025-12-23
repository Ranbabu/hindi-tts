#!/usr/bin/env bash
chmod +x ./piper/piper
uvicorn app:app --host 0.0.0.0 --port $PORT
