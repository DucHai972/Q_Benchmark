#!/usr/bin/env python3
"""
Script to check if TTL format in rule_based_querying is consistent with answer_lookup format.
This script verifies that the TTL files already have the correct format.
"""

import os

def check_ttl_format_consistency():
    """Check if rule_based_querying TTL files are already consistent with answer_lookup format"""
    
    ttl_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/rule_based_querying/ttl'
    answer_lookup_ttl_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_lookup/ttl/case_1.ttl'
    
    if not os.path.exists(ttl_base_path):
        print(f"Error: TTL directory not found: {ttl_base_path}")
        return
    
    if not os.path.exists(answer_lookup_ttl_path):
        print(f"Error: Answer lookup TTL reference file not found: {answer_lookup_ttl_path}")
        return
    
    # Read the reference format
    with open(answer_lookup_ttl_path, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    
    # Check key format indicators from reference
    reference_indicators = [
        '@prefix : <http://example.org/survey#>',
        '@prefix pred: <http://example.org/predicate#>',
        '@prefix qg: <http://example.org/question_group#>',
        'pred:BaseQuestion',
        'qg:hasSubQuestion',
        'pred:hasGroupResponse'
    ]
    
    # Get all TTL files 
    ttl_files = [f for f in os.listdir(ttl_base_path) if f.endswith('.ttl')]
    
    print(f"Checking {len(ttl_files)} TTL files in rule_based_querying...")
    
    consistent_files = 0
    inconsistent_files = 0
    
    for ttl_file in sorted(ttl_files):
        ttl_file_path = os.path.join(ttl_base_path, ttl_file)
        
        try:
            with open(ttl_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if all reference indicators are present
            missing_indicators = []
            for indicator in reference_indicators:
                if indicator not in content:
                    missing_indicators.append(indicator)
            
            if not missing_indicators:
                consistent_files += 1
                print(f"✓ {ttl_file}: Format is consistent with answer_lookup")
            else:
                inconsistent_files += 1
                print(f"✗ {ttl_file}: Missing indicators: {', '.join(missing_indicators)}")
        
        except Exception as e:
            print(f"Error checking {ttl_file}: {str(e)}")
            inconsistent_files += 1
    
    print(f"\nFormat consistency check complete!")
    print(f"- Total files checked: {len(ttl_files)}")
    print(f"- Files with consistent format: {consistent_files}")
    print(f"- Files with inconsistent format: {inconsistent_files}")
    
    if inconsistent_files == 0:
        print(f"\n✅ All TTL files in rule_based_querying are already consistent with answer_lookup format!")
        print(f"- All files use correct namespaces (pred:, qg:)")
        print(f"- All files use correct question structure with pred:BaseQuestion and qg:hasSubQuestion")
        print(f"- All files use correct response format with pred:hasGroupResponse")
        print(f"- No format standardization needed!")
    else:
        print(f"\n❌ {inconsistent_files} files need format standardization")

if __name__ == "__main__":
    check_ttl_format_consistency()