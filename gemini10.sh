#!/bin/bash
# Google Key 10 (geminisub01) - Cases 38-41
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_10"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 38 --max-cases 4