#!/usr/bin/env python3
"""
Script to fix respondent IDs in rule_based_querying TTL files from Rxx to Respondentxx format
to match answer_lookup format consistency.
"""

import os
import re

def fix_respondent_ids_in_ttl(file_path):
    """Fix respondent IDs from :Rxx to :Respondentxx format in TTL file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match :R followed by digits (respondent IDs)
    # This will match :R53, :R131, etc. and their associated group names like :R53_Parental_Education
    
    # Find all respondent IDs in the format :Rxx
    respondent_pattern = r':R(\d+)(?=\s|_|$)'
    respondent_matches = re.findall(respondent_pattern, content)
    
    changes_made = 0
    
    if respondent_matches:
        # Get unique respondent numbers
        unique_respondent_nums = set(respondent_matches)
        
        for respondent_num in unique_respondent_nums:
            # Replace all occurrences of :R{num} with :Respondent{num}
            old_pattern = f':R{respondent_num}'
            new_pattern = f':Respondent{respondent_num}'
            
            # Count occurrences before replacement
            count_before = content.count(old_pattern)
            
            if count_before > 0:
                # Replace all occurrences
                content = content.replace(old_pattern, new_pattern)
                changes_made += count_before
                print(f"  - Fixed {count_before} occurrences of :R{respondent_num} → :Respondent{respondent_num}")
    
    # Write the fixed content back to file
    if changes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    else:
        return 0

def process_all_rule_based_querying_ttl_files():
    """Process all TTL files in rule_based_querying to fix respondent IDs"""
    ttl_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/rule_based_querying/ttl'
    
    if not os.path.exists(ttl_base_path):
        print(f"Error: TTL directory not found: {ttl_base_path}")
        return
    
    # Get all TTL files
    ttl_files = [f for f in os.listdir(ttl_base_path) if f.endswith('.ttl')]
    
    print(f"Processing {len(ttl_files)} TTL files in rule_based_querying...")
    
    processed_count = 0
    total_changes = 0
    files_with_changes = 0
    
    for ttl_file in sorted(ttl_files):
        ttl_file_path = os.path.join(ttl_base_path, ttl_file)
        
        print(f"Processing {ttl_file}:")
        
        try:
            changes_made = fix_respondent_ids_in_ttl(ttl_file_path)
            
            if changes_made > 0:
                files_with_changes += 1
                total_changes += changes_made
                print(f"  ✓ Fixed {changes_made} respondent ID references")
            else:
                print(f"  ✓ No changes needed (already correct format)")
            
        except Exception as e:
            print(f"  ✗ Error processing {ttl_file}: {str(e)}")
        
        processed_count += 1
    
    print(f"\n" + "="*60)
    print(f"Processing complete!")
    print(f"- Total files processed: {processed_count}")
    print(f"- Files with changes: {files_with_changes}")
    print(f"- Files without changes: {processed_count - files_with_changes}")
    print(f"- Total respondent ID references fixed: {total_changes}")
    
    if files_with_changes > 0:
        print(f"\n✅ Successfully standardized respondent IDs in rule_based_querying TTL format!")
        print(f"- Changed :Rxx format to :Respondentxx format")
        print(f"- Format now matches answer_lookup TTL structure")
        print(f"- All respondent references and group associations updated")
    else:
        print(f"\n✅ All TTL files already had correct respondent ID format.")

if __name__ == "__main__":
    process_all_rule_based_querying_ttl_files()