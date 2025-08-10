import os
import pandas as pd
from pathlib import Path
import glob

def count_blank_responses(base_dir):
    """Count blank Response values in CSV files for gpt-4.1-mini and its variants"""
    
    results = {}
    
    # Find all gpt-4.1-mini directories (base and variants)
    gpt_dirs = [d for d in os.listdir(base_dir) if d.startswith('gpt-4.1-mini')]
    
    for model_dir in sorted(gpt_dirs):
        full_path = os.path.join(base_dir, model_dir)
        if not os.path.isdir(full_path):
            continue
            
        print(f"Processing {model_dir}...")
        results[model_dir] = {}
        
        # Find all CSV files in the directory tree
        csv_files = glob.glob(os.path.join(full_path, '**/*.csv'), recursive=True)
        
        for csv_file in csv_files:
            try:
                # Read CSV file
                df = pd.read_csv(csv_file)
                
                # Check if Response column exists
                if 'Response' not in df.columns:
                    continue
                
                # Count blank/empty Response values
                # Check for NaN, empty strings, and whitespace-only strings
                blank_count = df['Response'].isna().sum() + (df['Response'].astype(str).str.strip() == '').sum()
                total_rows = len(df)
                
                # Extract relative path for cleaner output
                rel_path = os.path.relpath(csv_file, full_path)
                results[model_dir][rel_path] = {
                    'blank_responses': blank_count,
                    'total_rows': total_rows,
                    'percentage': (blank_count / total_rows * 100) if total_rows > 0 else 0
                }
                
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")
                continue
    
    return results

def print_summary(results):
    """Print a summary of the results"""
    print("\n" + "="*80)
    print("SUMMARY OF BLANK RESPONSES IN gpt-4.1-mini AND VARIANTS")
    print("="*80)
    
    for model_dir, files in results.items():
        if not files:
            print(f"\n{model_dir}: No CSV files with Response column found")
            continue
            
        total_blank = sum(file_data['blank_responses'] for file_data in files.values())
        total_rows = sum(file_data['total_rows'] for file_data in files.values())
        overall_percentage = (total_blank / total_rows * 100) if total_rows > 0 else 0
        
        print(f"\n{model_dir}:")
        print(f"  Total blank responses: {total_blank}")
        print(f"  Total rows: {total_rows}")
        print(f"  Overall percentage: {overall_percentage:.2f}%")
        print(f"  Files processed: {len(files)}")
        
        # Show files with blank responses
        files_with_blanks = {k: v for k, v in files.items() if v['blank_responses'] > 0}
        if files_with_blanks:
            print(f"  Files with blank responses:")
            for file_path, data in files_with_blanks.items():
                print(f"    {file_path}: {data['blank_responses']}/{data['total_rows']} ({data['percentage']:.1f}%)")

if __name__ == "__main__":
    base_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_results"
    results = count_blank_responses(base_dir)
    print_summary(results)