#!/bin/bash
# Google Key 11 (geminisub03) - Cases 42-50
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_11"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 42 --max-cases 9