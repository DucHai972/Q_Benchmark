#!/usr/bin/env python3
"""
Script to check for missing responses or cases in benchmark_results/gpt-5-mini
for cases 2-50 across all datasets, tasks, and formats.
"""

import os
import csv
import sys
from collections import defaultdict

def check_missing_responses(base_dir="benchmark_results/gpt-5-mini"):
    """Check for missing responses or cases in the specified directory."""
    
    datasets = ["healthcare-dataset", "isbar", "self-reported-mental-health", "stack-overflow-2022", "sus-uta7"]
    tasks = ["answer_lookup", "answer_reverse_lookup", "conceptual_aggregation", 
             "multi_hop_relational_inference", "respondent_count", "rule_based_querying"]
    formats = ["html", "json", "md", "ttl", "txt", "xml"]
    
    missing_results = []
    file_issues = []
    
    for dataset in datasets:
        for task in tasks:
            for format_type in formats:
                file_path = os.path.join(base_dir, dataset, task, f"{task}_{format_type}_converted_prompts.csv")
                
                if not os.path.exists(file_path):
                    file_issues.append({
                        'type': 'file_missing',
                        'dataset': dataset,
                        'task': task,
                        'format': format_type,
                        'file_path': file_path
                    })
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader)
                        
                        # Find column indices
                        case_id_idx = header.index('case_id') if 'case_id' in header else None
                        response_idx = header.index('Response') if 'Response' in header else None
                        
                        if case_id_idx is None:
                            file_issues.append({
                                'type': 'missing_case_id_column',
                                'dataset': dataset,
                                'task': task,
                                'format': format_type,
                                'file_path': file_path
                            })
                            continue
                            
                        if response_idx is None:
                            file_issues.append({
                                'type': 'missing_response_column',
                                'dataset': dataset,
                                'task': task,
                                'format': format_type,
                                'file_path': file_path
                            })
                            continue
                        
                        # Track which cases exist and which have responses
                        existing_cases = set()
                        cases_with_responses = set()
                        
                        for row in reader:
                            if len(row) > case_id_idx:
                                case_id = row[case_id_idx].strip()
                                existing_cases.add(case_id)
                                
                                # Check if response exists and is not empty
                                if (len(row) > response_idx and 
                                    row[response_idx] and 
                                    row[response_idx].strip()):
                                    cases_with_responses.add(case_id)
                        
                        # Check for missing cases and responses in range 2-50
                        expected_cases = {f"case_{i}" for i in range(2, 51)}
                        missing_cases = expected_cases - existing_cases
                        missing_responses = (expected_cases & existing_cases) - cases_with_responses
                        
                        if missing_cases:
                            missing_results.append({
                                'type': 'missing_cases',
                                'dataset': dataset,
                                'task': task,
                                'format': format_type,
                                'file_path': file_path,
                                'missing_cases': sorted(missing_cases, key=lambda x: int(x.split('_')[1]))
                            })
                        
                        if missing_responses:
                            missing_results.append({
                                'type': 'missing_responses',
                                'dataset': dataset,
                                'task': task,
                                'format': format_type,
                                'file_path': file_path,
                                'missing_responses': sorted(missing_responses, key=lambda x: int(x.split('_')[1]))
                            })
                            
                except Exception as e:
                    file_issues.append({
                        'type': 'file_read_error',
                        'dataset': dataset,
                        'task': task,
                        'format': format_type,
                        'file_path': file_path,
                        'error': str(e)
                    })
    
    return missing_results, file_issues

def print_results(missing_results, file_issues):
    """Print the results in a readable format."""
    
    print("=" * 80)
    print("MISSING RESPONSES/CASES CHECK FOR GPT-5-MINI (Cases 2-50)")
    print("=" * 80)
    
    if file_issues:
        print("\n🚨 FILE ISSUES:")
        print("-" * 40)
        for issue in file_issues:
            print(f"  {issue['type'].upper()}")
            print(f"    Dataset: {issue['dataset']}")
            print(f"    Task: {issue['task']}")
            print(f"    Format: {issue['format']}")
            if 'error' in issue:
                print(f"    Error: {issue['error']}")
            print()
    
    if missing_results:
        print("\n📊 MISSING DATA SUMMARY:")
        print("-" * 40)
        
        # Group by type
        missing_cases = [r for r in missing_results if r['type'] == 'missing_cases']
        missing_responses = [r for r in missing_results if r['type'] == 'missing_responses']
        
        if missing_cases:
            print(f"\n🔍 MISSING CASES ({len(missing_cases)} files affected):")
            for result in missing_cases:
                print(f"  📁 {result['dataset']} > {result['task']} > {result['format']}")
                print(f"     Missing: {', '.join(result['missing_cases'])}")
        
        if missing_responses:
            print(f"\n❌ MISSING RESPONSES ({len(missing_responses)} files affected):")
            for result in missing_responses:
                print(f"  📁 {result['dataset']} > {result['task']} > {result['format']}")
                print(f"     Missing: {', '.join(result['missing_responses'])}")
    
    if not missing_results and not file_issues:
        print("\n✅ ALL CHECKS PASSED!")
        print("All expected cases (2-50) exist and have responses in all files.")
    
    print("\n" + "=" * 80)

def generate_summary_stats(missing_results, file_issues):
    """Generate summary statistics."""
    total_files_expected = 5 * 6 * 6  # 5 datasets × 6 tasks × 6 formats = 180 files
    
    files_with_missing_cases = len([r for r in missing_results if r['type'] == 'missing_cases'])
    files_with_missing_responses = len([r for r in missing_results if r['type'] == 'missing_responses'])
    files_with_issues = len(file_issues)
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"  Total expected files: {total_files_expected}")
    print(f"  Files with missing cases: {files_with_missing_cases}")
    print(f"  Files with missing responses: {files_with_missing_responses}")
    print(f"  Files with other issues: {files_with_issues}")
    
    # Count by dataset
    dataset_stats = defaultdict(int)
    for result in missing_results:
        dataset_stats[result['dataset']] += 1
    
    if dataset_stats:
        print(f"\n📊 ISSUES BY DATASET:")
        for dataset, count in sorted(dataset_stats.items()):
            print(f"  {dataset}: {count} files with issues")

if __name__ == "__main__":
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    missing_results, file_issues = check_missing_responses()
    print_results(missing_results, file_issues)
    generate_summary_stats(missing_results, file_issues)