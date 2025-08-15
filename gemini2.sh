#!/bin/bash
# Google Key 2 (z01) - Cases 6-9
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_2"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 6 --max-cases 4