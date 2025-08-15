#!/bin/bash
# OpenAI Key 8 (sub03) - Cases 30-33
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_8"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 30 --max-cases 4