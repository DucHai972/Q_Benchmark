#!/usr/bin/env python3
"""
Script to fix TTL respondent naming from :Rxx format to :Respondentxx format
in self-reported-mental-health answer_lookup task
"""

import os
import re

def fix_ttl_respondent_naming(ttl_content):
    """
    Fix TTL respondent naming from :Rxx to :Respondentxx format
    """
    # Pattern to match :R followed by digits (respondent IDs)
    # This will match :R73, :R85, :R129, etc.
    pattern = r':R(\d+)'
    
    # Replace with :Respondent + the number
    fixed_content = re.sub(pattern, r':Respondent\1', ttl_content)
    
    return fixed_content

def process_all_ttl_files():
    """Process all TTL files in self-reported-mental-health answer_lookup"""
    base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_lookup/ttl'
    
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
        
        # Fix the respondent naming
        fixed_content = fix_ttl_respondent_naming(original_content)
        
        # Check if changes were made
        if fixed_content != original_content:
            changes_made += 1
            
            # Count the number of replacements made
            original_matches = re.findall(r':R(\d+)', original_content)
            fixed_matches = re.findall(r':Respondent(\d+)', fixed_content)
            
            print(f"Processing {ttl_file}: {len(original_matches)} respondent references updated")
            
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
        print(f"\nSuccessfully updated TTL respondent naming from :Rxx to :Respondentxx format!")
    else:
        print(f"\nAll files already had correct respondent naming format.")

if __name__ == "__main__":
    process_all_ttl_files()