#!/bin/bash
# Google Key 1 (reliable) - Cases 2-5
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_1"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 2 --max-cases 4