#!/bin/bash
# OpenAI Key 7 (sub02) - Cases 26-29
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_7"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 26 --max-cases 4