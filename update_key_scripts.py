#!/usr/bin/env python3

# Script to update all key scripts with the correct .env handling

scripts = {
    'key2.sh': {'key': 2, 'start_case': 6, 'max_cases': 4, 'label': 'z01'},
    'key3.sh': {'key': 3, 'start_case': 10, 'max_cases': 4, 'label': '9722'},
    'key4.sh': {'key': 4, 'start_case': 14, 'max_cases': 4, 'label': '1251'},
    'key5.sh': {'key': 5, 'start_case': 18, 'max_cases': 4, 'label': 'insight'},
    'key6.sh': {'key': 6, 'start_case': 22, 'max_cases': 4, 'label': 'sub01'},
    'key7.sh': {'key': 7, 'start_case': 26, 'max_cases': 4, 'label': 'sub02'},
    'key8.sh': {'key': 8, 'start_case': 30, 'max_cases': 4, 'label': 'sub03'},
    'key9.sh': {'key': 9, 'start_case': 34, 'max_cases': 4, 'label': 'sub04'},
    'key10.sh': {'key': 10, 'start_case': 38, 'max_cases': 4, 'label': 'sub05'},
    'key11.sh': {'key': 11, 'start_case': 42, 'max_cases': 9, 'label': 'sub06'},
}

for script_name, config in scripts.items():
    content = f"""#!/bin/bash
# OpenAI Key {config['key']} ({config['label']}) - Cases {config['start_case']}-{config['start_case'] + config['max_cases'] - 1}
set -a && source .env && set +a
export OPENAI_API_KEY="$OPENAI_API_KEY_{config['key']}"
source .venv/bin/activate && python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --start-case {config['start_case']} --max-cases {config['max_cases']}"""
    
    with open(script_name, 'w') as f:
        f.write(content)
    
    print(f"Updated {script_name}")

print("All key scripts updated!")