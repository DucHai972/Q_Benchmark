#!/bin/bash
# OpenAI Key 5 (insight) - Cases 18-21
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_5"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 18 --max-cases 4