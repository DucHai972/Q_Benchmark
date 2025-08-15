#!/bin/bash
# Google Key 3 (9722) - Cases 10-13
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_3"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 10 --max-cases 4