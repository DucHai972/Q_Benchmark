#!/usr/bin/env python3
"""
Batch update prompt format in all advanced_prompts files
"""

import json
import os
from pathlib import Path

def update_file(file_path):
    """Update a single JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            data = [data]
        
        updated = False
        for item in data:
            if 'prompt' in item:
                old_prompt = item['prompt']
                # Check if it needs updating (contains the old format)
                if '[ROLE_PROMPTING]' in old_prompt and '<role>' not in old_prompt:
                    new_prompt = (
                        "<example>\\n[CASE_1]\\n</example>\\n\\n"
                        "<questionnaire>\\n[questionnaire]\\n</questionnaire>\\n\\n"
                        "<role>\\n[ROLE_PROMPTING]\\n</role>\\n\\n"
                        "<format>\\n[FORMAT_EXPLANATION]\\n</format>\\n\\n"
                        "<output>\\n[OUTPUT_INSTRUCTIONS]\\n</output>\\n\\n"
                        "<task>\\n[question]\\n</task>"
                    )
                    item['prompt'] = new_prompt
                    updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

# List of all files to update
files_to_update = [
    # isbar
    "advanced_prompts/isbar/isbar_answer_reverse_lookup_qa_pairs.json",
    "advanced_prompts/isbar/isbar_conceptual_aggregation_qa_pairs.json", 
    "advanced_prompts/isbar/isbar_multi_hop_relational_inference_qa_pairs.json",
    "advanced_prompts/isbar/isbar_respondent_count_qa_pairs.json",
    "advanced_prompts/isbar/isbar_rule_based_querying_qa_pairs.json",
    
    # self-reported-mental-health
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_answer_lookup_qa_pairs.json",
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_answer_reverse_lookup_qa_pairs.json",
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_conceptual_aggregation_qa_pairs.json",
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_multi_hop_relational_inference_qa_pairs.json",
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_respondent_count_qa_pairs.json",
    "advanced_prompts/self-reported-mental-health/self-reported-mental-health_rule_based_querying_qa_pairs.json",
    
    # stack-overflow-2022
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_answer_lookup_qa_pairs.json",
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_answer_reverse_lookup_qa_pairs.json",
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_conceptual_aggregation_qa_pairs.json",
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_multi_hop_relational_inference_qa_pairs.json",
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_respondent_count_qa_pairs.json",
    "advanced_prompts/stack-overflow-2022/stack-overflow-2022_rule_based_querying_qa_pairs.json",
    
    # sus-uta7
    "advanced_prompts/sus-uta7/sus-uta7_answer_lookup_qa_pairs.json",
    "advanced_prompts/sus-uta7/sus-uta7_answer_reverse_lookup_qa_pairs.json",
    "advanced_prompts/sus-uta7/sus-uta7_conceptual_aggregation_qa_pairs.json",
    "advanced_prompts/sus-uta7/sus-uta7_multi_hop_relational_inference_qa_pairs.json",
    "advanced_prompts/sus-uta7/sus-uta7_respondent_count_qa_pairs.json",
    "advanced_prompts/sus-uta7/sus-uta7_rule_based_querying_qa_pairs.json"
]

updated_count = 0
total_count = len(files_to_update)

for file_path in files_to_update:
    if os.path.exists(file_path):
        if update_file(file_path):
            updated_count += 1
            print(f"✅ Updated: {file_path}")
        else:
            print(f"ℹ️ No update needed: {file_path}")
    else:
        print(f"❌ File not found: {file_path}")

print(f"\\nBatch update complete: {updated_count}/{total_count} files updated")