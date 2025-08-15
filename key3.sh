#!/bin/bash
# OpenAI Key 3 (9722) - Cases 10-13
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_3"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case 10 --max-cases 4