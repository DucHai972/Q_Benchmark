#!/bin/bash
# Google Key 9 (sub05) - Cases 34-37
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_9"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 34 --max-cases 4