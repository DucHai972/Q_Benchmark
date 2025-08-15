#!/bin/bash
# Google Key 8 (sub04) - Cases 30-33
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_8"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case 30 --max-cases 4