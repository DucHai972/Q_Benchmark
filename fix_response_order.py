#!/usr/bin/env python3

import re
from pathlib import Path

def fix_response_order(file_path):
    """Fix the order of response sections to match case_1 format."""
    
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip case_1 and case_1_modified as they already have correct order
    if 'case_1.ttl' in str(file_path) or 'case_1_modified.ttl' in str(file_path):
        print(f"  Skipping {file_path} - already has correct order")
        return
    
    # Pattern to match each respondent block
    respondent_pattern = r'(:R\d+) pred:Year_of_birth.*?(?=:R\d+|$)'
    
    def reorder_respondent(match):
        respondent_block = match.group(0)
        respondent_id_match = re.search(r':R(\d+)', respondent_block)
        if not respondent_id_match:
            return respondent_block
            
        respondent_id = respondent_id_match.group(1)
        
        # Extract different sections
        # 1. Basic demographics (Year_of_birth through Ethnic_identity)
        basic_demo_pattern = r'(:R' + respondent_id + r') pred:Year_of_birth.*?pred:Ethnic_identity [0-9.]+\s*\.'
        basic_demo_match = re.search(basic_demo_pattern, respondent_block, re.DOTALL)
        
        # 2. Parental Education group
        parental_pattern = r':R' + respondent_id + r'_Parental_Education.*?:R' + respondent_id + r' pred:hasGroupResponse :R' + respondent_id + r'_Parental_Education \.'
        parental_match = re.search(parental_pattern, respondent_block, re.DOTALL)
        
        # 3. Life satisfaction questions (Life_satisfaction through Loneliness)
        life_sat_pattern = r'(:R' + respondent_id + r') pred:Life_satisfaction.*?pred:Loneliness [0-9.]+\s*\.'
        life_sat_match = re.search(life_sat_pattern, respondent_block, re.DOTALL)
        
        # 4. Emotional Regulation group
        emotional_pattern = r':R' + respondent_id + r'_Emotional_Regulation_Frequency.*?:R' + respondent_id + r' pred:hasGroupResponse :R' + respondent_id + r'_Emotional_Regulation_Frequency \.'
        emotional_match = re.search(emotional_pattern, respondent_block, re.DOTALL)
        
        # 5. Anxiety group
        anxiety_pattern = r':R' + respondent_id + r'_Anxiety_Symptoms_Frequency.*?:R' + respondent_id + r' pred:hasGroupResponse :R' + respondent_id + r'_Anxiety_Symptoms_Frequency \.'
        anxiety_match = re.search(anxiety_pattern, respondent_block, re.DOTALL)
        
        # 6. Depressive group
        depressive_pattern = r':R' + respondent_id + r'_Depressive_Symptoms_Frequency.*?:R' + respondent_id + r' pred:hasGroupResponse :R' + respondent_id + r'_Depressive_Symptoms_Frequency \.'
        depressive_match = re.search(depressive_pattern, respondent_block, re.DOTALL)
        
        if not all([basic_demo_match, life_sat_match]):
            print(f"  Warning: Could not find all required sections for respondent {respondent_id}")
            return respondent_block
        
        # Build the correctly ordered response
        result = []
        
        # 1. Basic demographics
        result.append(basic_demo_match.group(0))
        result.append("")
        
        # 2. Parental Education (if exists)
        if parental_match:
            result.append(parental_match.group(0))
            result.append("")
        
        # 3. Life satisfaction questions
        result.append(life_sat_match.group(0))
        result.append("")
        
        # 4. Emotional Regulation (if exists)
        if emotional_match:
            result.append(emotional_match.group(0))
            result.append("")
        
        # 5. Anxiety (if exists)
        if anxiety_match:
            result.append(anxiety_match.group(0))
            result.append("")
        
        # 6. Depressive (if exists)
        if depressive_match:
            result.append(depressive_match.group(0))
            result.append("")
        
        return '\n'.join(result).rstrip() + '\n'
    
    # Apply reordering to all respondent blocks
    new_content = re.sub(respondent_pattern, reorder_respondent, content, flags=re.DOTALL)
    
    # Write back the corrected content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Successfully reordered response sections in {file_path}")

def main():
    """Fix response order in case_2 through case_50."""
    
    ttl_dir = Path("benchmark_cache/self-reported-mental-health/answer_lookup/ttl")
    
    if not ttl_dir.exists():
        print(f"Directory {ttl_dir} not found!")
        return
    
    # Get case_2 through case_50 files
    ttl_files = []
    for i in range(2, 51):
        case_file = ttl_dir / f"case_{i}.ttl"
        if case_file.exists():
            ttl_files.append(case_file)
    
    print(f"Found {len(ttl_files)} TTL files to fix (case_2 through case_50)...")
    
    for ttl_file in sorted(ttl_files):
        try:
            fix_response_order(ttl_file)
        except Exception as e:
            print(f"  ERROR processing {ttl_file}: {e}")
    
    print("Response order fixing complete!")

if __name__ == "__main__":
    main()