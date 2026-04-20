#!/bin/bash
source ../../.venv/bin/activate
uvicorn main:app --reload --port 8001 2>&1 | tee latest.log
