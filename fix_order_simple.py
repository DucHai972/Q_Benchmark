#!/usr/bin/env python3

import re
from pathlib import Path

def fix_response_order_simple(file_path):
    """Fix the order of response sections using a simpler approach."""
    
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip case_1 and case_1_modified as they already have correct order
    if 'case_1.ttl' in str(file_path) or 'case_1_modified.ttl' in str(file_path):
        print(f"  Skipping {file_path} - already has correct order")
        return
    
    # Split content into before responses and responses section
    responses_start = content.find('# Responses')
    if responses_start == -1:
        print(f"  Warning: Could not find '# Responses' section in {file_path}")
        return
    
    before_responses = content[:responses_start]
    responses_section = content[responses_start:]
    
    # For each respondent, we need to reorder the sections
    # Find all respondent blocks
    respondent_blocks = []
    lines = responses_section.split('\n')
    current_block = []
    current_respondent = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a new respondent
        if line.startswith(':R') and ' pred:Year_of_birth' in line:
            # If we have a previous block, save it
            if current_block and current_respondent:
                respondent_blocks.append((current_respondent, '\n'.join(current_block)))
            
            # Start new block
            current_respondent = line.split()[0]
            current_block = [lines[i]]
        elif current_block:
            current_block.append(lines[i])
        
        i += 1
    
    # Don't forget the last block
    if current_block and current_respondent:
        respondent_blocks.append((current_respondent, '\n'.join(current_block)))
    
    print(f"  Found {len(respondent_blocks)} respondent blocks")
    
    # Process each respondent block
    fixed_blocks = []
    for respondent_id, block in respondent_blocks:
        fixed_block = reorder_respondent_block(respondent_id, block)
        fixed_blocks.append(fixed_block)
    
    # Reconstruct the file
    new_content = before_responses + '# Responses\n' + '\n\n'.join(fixed_blocks) + '\n'
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Successfully reordered {file_path}")

def reorder_respondent_block(respondent_id, block):
    """Reorder sections within a single respondent block."""
    
    lines = block.split('\n')
    
    # Find different sections
    basic_demo_lines = []
    parental_education_lines = []
    life_satisfaction_lines = []
    emotional_regulation_lines = []
    anxiety_lines = []
    depressive_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # Basic demographics (Year_of_birth through Ethnic_identity)
        if ' pred:Year_of_birth' in line:
            # Collect all basic demo lines until we hit the period
            basic_demo_lines.append(lines[i])
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(' .'):
                basic_demo_lines.append(lines[i])
                i += 1
            if i < len(lines):
                basic_demo_lines.append(lines[i])  # Add the line ending with period
                i += 1
                
        # Parental Education group
        elif '_Parental_Education' in line and ' pred:Father' in line:
            # Collect parental education group
            parental_education_lines.append(lines[i])
            i += 1
            while i < len(lines) and not ('pred:hasGroupResponse' in lines[i] and '_Parental_Education' in lines[i]):
                parental_education_lines.append(lines[i])
                i += 1
            if i < len(lines):
                parental_education_lines.append(lines[i])  # Add hasGroupResponse line
                i += 1
                
        # Life satisfaction (Life_satisfaction through Loneliness)
        elif ' pred:Life_satisfaction' in line:
            # Collect life satisfaction lines until we hit the period after Loneliness
            life_satisfaction_lines.append(lines[i])
            i += 1
            while i < len(lines) and not ('pred:Loneliness' in lines[i] and lines[i].strip().endswith(' .')):
                life_satisfaction_lines.append(lines[i])
                i += 1
            if i < len(lines):
                life_satisfaction_lines.append(lines[i])  # Add the Loneliness line
                i += 1
                
        # Emotional Regulation group
        elif '_Emotional_Regulation_Frequency' in line and ' pred:' in line:
            # Collect emotional regulation group
            emotional_regulation_lines.append(lines[i])
            i += 1
            while i < len(lines) and not ('pred:hasGroupResponse' in lines[i] and '_Emotional_Regulation_Frequency' in lines[i]):
                emotional_regulation_lines.append(lines[i])
                i += 1
            if i < len(lines):
                emotional_regulation_lines.append(lines[i])  # Add hasGroupResponse line
                i += 1
                
        # Anxiety group
        elif '_Anxiety_Symptoms_Frequency' in line and ' pred:' in line:
            # Collect anxiety group
            anxiety_lines.append(lines[i])
            i += 1
            while i < len(lines) and not ('pred:hasGroupResponse' in lines[i] and '_Anxiety_Symptoms_Frequency' in lines[i]):
                anxiety_lines.append(lines[i])
                i += 1
            if i < len(lines):
                anxiety_lines.append(lines[i])  # Add hasGroupResponse line
                i += 1
                
        # Depressive group
        elif '_Depressive_Symptoms_Frequency' in line and ' pred:' in line:
            # Collect depressive group
            depressive_lines.append(lines[i])
            i += 1
            while i < len(lines) and not ('pred:hasGroupResponse' in lines[i] and '_Depressive_Symptoms_Frequency' in lines[i]):
                depressive_lines.append(lines[i])
                i += 1
            if i < len(lines):
                depressive_lines.append(lines[i])  # Add hasGroupResponse line
                i += 1
        else:
            i += 1
    
    # Build the correctly ordered block
    result = []
    
    # 1. Basic demographics
    if basic_demo_lines:
        result.extend(basic_demo_lines)
        result.append('')
    
    # 2. Parental Education
    if parental_education_lines:
        result.extend(parental_education_lines)
        result.append('')
    
    # 3. Life satisfaction
    if life_satisfaction_lines:
        result.extend(life_satisfaction_lines)
        result.append('')
    
    # 4. Emotional Regulation
    if emotional_regulation_lines:
        result.extend(emotional_regulation_lines)
        result.append('')
    
    # 5. Anxiety
    if anxiety_lines:
        result.extend(anxiety_lines)
        result.append('')
    
    # 6. Depressive
    if depressive_lines:
        result.extend(depressive_lines)
        result.append('')
    
    return '\n'.join(result).rstrip()

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
            fix_response_order_simple(ttl_file)
        except Exception as e:
            print(f"  ERROR processing {ttl_file}: {e}")
    
    print("Response order fixing complete!")

if __name__ == "__main__":
    main()