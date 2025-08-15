#!/usr/bin/env python3

# Script to create Gemini key scripts with the same distribution as OpenAI

scripts = {
    'gemini1.sh': {'key': 1, 'start_case': 2, 'max_cases': 4, 'label': 'reliable'},
    'gemini2.sh': {'key': 2, 'start_case': 6, 'max_cases': 4, 'label': 'z01'},
    'gemini3.sh': {'key': 3, 'start_case': 10, 'max_cases': 4, 'label': '9722'},
    'gemini4.sh': {'key': 4, 'start_case': 14, 'max_cases': 4, 'label': 'sub01'},
    'gemini5.sh': {'key': 5, 'start_case': 18, 'max_cases': 4, 'label': 'sub02'},
    'gemini6.sh': {'key': 6, 'start_case': 22, 'max_cases': 4, 'label': 'sub03'},
    'gemini7.sh': {'key': 7, 'start_case': 26, 'max_cases': 4, 'label': 'qvt'},
    'gemini8.sh': {'key': 8, 'start_case': 30, 'max_cases': 4, 'label': 'sub04'},
    'gemini9.sh': {'key': 9, 'start_case': 34, 'max_cases': 4, 'label': 'sub05'},
    'gemini10.sh': {'key': 10, 'start_case': 38, 'max_cases': 4, 'label': 'geminisub01'},
    'gemini11.sh': {'key': 11, 'start_case': 42, 'max_cases': 9, 'label': 'geminisub03'},
}

for script_name, config in scripts.items():
    content = f"""#!/bin/bash
# Google Key {config['key']} ({config['label']}) - Cases {config['start_case']}-{config['start_case'] + config['max_cases'] - 1}
set -a && source .env && set +a
export GOOGLE_API_KEY="$GOOGLE_API_KEY_{config['key']}"
source .venv/bin/activate && python3 benchmark_pipeline.py --model google --google-model gemini-2.5-flash --start-case {config['start_case']} --max-cases {config['max_cases']}"""
    
    with open(script_name, 'w') as f:
        f.write(content)
    
    print(f"Created {script_name}")

print("All Gemini key scripts created!")