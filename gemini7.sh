#!/bin/bash
# Google Key 7 (qvt) - Cases 26-29
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_7"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 26 --max-cases 4