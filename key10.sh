#!/bin/bash
# OpenAI Key 10 (sub05) - Cases 38-41
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_10"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 38 --max-cases 4