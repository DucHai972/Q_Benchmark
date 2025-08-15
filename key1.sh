#!/bin/bash
# OpenAI Key 1 (reliable) - Cases 2-5
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_1"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 2 --max-cases 4