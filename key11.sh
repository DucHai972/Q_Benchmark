#!/bin/bash
# OpenAI Key 11 (sub06) - Cases 42-50
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_11"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 42 --max-cases 9