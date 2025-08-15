#!/bin/bash
# Google Key 5 (sub02) - Cases 18-21
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_5"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 18 --max-cases 4