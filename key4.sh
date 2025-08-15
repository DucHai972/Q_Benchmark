#!/bin/bash
# OpenAI Key 4 (1251) - Cases 14-17
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_4"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 14 --max-cases 4