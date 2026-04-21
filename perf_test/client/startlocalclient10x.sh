#!/bin/bash
source ../../.venv/bin/activate
python3 benchmark10x.py 2>&1 | tee result10x.txt
