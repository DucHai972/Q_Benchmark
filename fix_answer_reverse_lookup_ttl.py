#!/usr/bin/env python3
"""
Script to fix TTL format in answer_reverse_lookup to match answer_lookup format
1. Change respondent naming from :Rxx to :Respondentxx  
2. Fix formatting to match answer_lookup style
"""

import os
import re

def fix_ttl_formatting_and_respondents(ttl_content):
    """
    Fix TTL content to match answer_lookup format:
    1. Change :Rxx to :Respondentxx
    2. Fix formatting of qg:hasSubQuestion statements
    """
    
    # Step 1: Fix respondent naming from :Rxx to :Respondentxx
    # This will match :R followed by digits (respondent IDs)
    respondent_pattern = r':R(\d+)'
    ttl_content = re.sub(respondent_pattern, r':Respondent\1', ttl_content)
    
    # Step 2: Fix formatting of qg:hasSubQuestion statements
    # Look for patterns like: qg:hasSubQuestion :QSomething,    qg:hasSubQuestion :QOther,
    # Replace with proper multi-line formatting
    
    # Find all qg:hasSubQuestion lines that have multiple items on one line
    hasSubQuestion_pattern = r'(qg:hasSubQuestion [^.;]+)(\s*\.)'
    
    def format_hasSubQuestion(match):
        content = match.group(1)
        ending = match.group(2)
        
        # Split by comma and clean up
        parts = content.split('qg:hasSubQuestion')
        if len(parts) <= 1:
            return match.group(0)  # No changes needed
            
        # First part should be empty or whitespace
        formatted_parts = []
        for i, part in enumerate(parts[1:], 1):  # Skip the first empty part
            part = part.strip().rstrip(',').strip()
            if part:
                if i == 1:
                    formatted_parts.append(f'    qg:hasSubQuestion {part}')
                else:
                    formatted_parts.append(f'                      {part}')
        
        if formatted_parts:
            # Add comma to all but the last item
            for i in range(len(formatted_parts) - 1):
                formatted_parts[i] += ','
            
            return '\n'.join(formatted_parts) + ' ' + ending.strip()
        
        return match.group(0)
    
    ttl_content = re.sub(hasSubQuestion_pattern, format_hasSubQuestion, ttl_content, flags=re.DOTALL)
    
    return ttl_content

def process_all_answer_reverse_lookup_ttl_files():
    """Process all TTL files in self-reported-mental-health answer_reverse_lookup"""
    base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_reverse_lookup/ttl'
    
    if not os.path.exists(base_path):
        print(f"Error: Directory not found: {base_path}")
        return
    
    # Get all TTL files
    ttl_files = [f for f in os.listdir(base_path) if f.endswith('.ttl')]
    
    print(f"Found {len(ttl_files)} TTL files to process...")
    
    processed_count = 0
    changes_made = 0
    
    for ttl_file in sorted(ttl_files):
        file_path = os.path.join(base_path, ttl_file)
        
        # Read the current content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Fix the formatting and respondent naming
        fixed_content = fix_ttl_formatting_and_respondents(original_content)
        
        # Check if changes were made
        if fixed_content != original_content:
            changes_made += 1
            
            # Count the number of respondent replacements made
            original_respondents = re.findall(r':R(\d+)', original_content)
            fixed_respondents = re.findall(r':Respondent(\d+)', fixed_content)
            
            print(f"Processing {ttl_file}: {len(set(original_respondents))} respondent IDs updated to :Respondent format")
            
            # Write the fixed content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
        else:
            print(f"Processing {ttl_file}: No changes needed")
        
        processed_count += 1
    
    print(f"\nProcessing complete!")
    print(f"- Total files processed: {processed_count}")
    print(f"- Files with changes: {changes_made}")
    print(f"- Files without changes: {processed_count - changes_made}")
    
    if changes_made > 0:
        print(f"\nSuccessfully updated answer_reverse_lookup TTL files to match answer_lookup format!")
        print(f"- Fixed respondent naming from :Rxx to :Respondentxx")
        print(f"- Improved formatting consistency")
    else:
        print(f"\nAll files already had correct format.")

if __name__ == "__main__":
    process_all_answer_reverse_lookup_ttl_files()