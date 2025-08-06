#!/usr/bin/env python3
"""
Script to update prompt format in all advanced_prompts files to use XML-style tags.
"""

import json
import os
from pathlib import Path

def update_prompt_format(file_path):
    """Update the prompt format in a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]
        
        updated = False
        for item in data:
            if 'prompt' in item:
                # New XML-style format
                new_prompt = (
                    "<example>\\n[CASE_1]\\n</example>\\n\\n"
                    "<questionnaire>\\n[questionnaire]\\n</questionnaire>\\n\\n"
                    "<role>\\n[ROLE_PROMPTING]\\n</role>\\n\\n"
                    "<format>\\n[FORMAT_EXPLANATION]\\n</format>\\n\\n"
                    "<output>\\n[OUTPUT_INSTRUCTIONS]\\n</output>\\n\\n"
                    "<task>\\n[question]\\n</task>"
                )
                
                if item['prompt'] != new_prompt:
                    item['prompt'] = new_prompt
                    updated = True
        
        if updated:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"ℹ️  No update needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all advanced prompts files"""
    advanced_prompts_dir = Path("advanced_prompts")
    
    if not advanced_prompts_dir.exists():
        print("❌ advanced_prompts directory not found")
        return
    
    # Find all JSON files in subdirectories
    json_files = list(advanced_prompts_dir.glob("*/*.json"))
    
    if not json_files:
        print("❌ No JSON files found in advanced_prompts")
        return
    
    print(f"Found {len(json_files)} advanced prompt files to update...")
    print()
    
    updated_count = 0
    total_count = len(json_files)
    
    for json_file in sorted(json_files):
        if update_prompt_format(json_file):
            updated_count += 1
    
    print()
    print(f"Update complete: {updated_count}/{total_count} files updated")

if __name__ == "__main__":
    main()