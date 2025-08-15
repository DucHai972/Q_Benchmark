#!/bin/bash
# OpenAI Key 9 (sub04) - Cases 34-37
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_9"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 34 --max-cases 4