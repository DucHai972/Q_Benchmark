#!/bin/bash
# Google Key 6 (sub03) - Cases 22-25
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_6"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 22 --max-cases 4