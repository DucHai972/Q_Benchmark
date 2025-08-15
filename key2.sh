#!/bin/bash
# OpenAI Key 2 (z01) - Cases 6-9
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_2"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 6 --max-cases 4