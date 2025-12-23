#!/usr/bin/env bash

echo "Starting Edge TTS Server..."
uvicorn app:app --host 0.0.0.0 --port $PORT
