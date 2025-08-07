#!/usr/bin/env python3
"""
Benchmark Results Analysis Script

This script analyzes the benchmark results from Q_Benchmark/benchmark_results/gpt-4.1-mini
and generates two tables:
1. Table showing correct/total counts for each data format and task combination
2. Table showing percentage correct for each data format and task combination

The script processes all CSV files in the benchmark results directory structure.
"""

import os
import csv
import glob
from collections import defaultdict

def analyze_benchmark_results(base_path):
    """
    Analyze benchmark results and generate summary tables.
    
    Args:
        base_path (str): Path to the benchmark results directory
    
    Returns:
        tuple: (count_table, percentage_table, results) - Analysis results
    """
    
    # Find all CSV files in the benchmark results
    csv_pattern = os.path.join(base_path, "**", "*.csv")
    csv_files = glob.glob(csv_pattern, recursive=True)
    
    print(f"Found {len(csv_files)} CSV files to analyze")
    
    # Initialize dictionaries to store results
    results = {}
    
    # Data formats and tasks we expect to find
    data_formats = ['html', 'json', 'md', 'ttl', 'txt', 'xml']
    tasks = set()
    datasets = set()
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Extract information from file path
            rel_path = os.path.relpath(csv_file, base_path)
            path_parts = rel_path.split(os.sep)
            
            if len(path_parts) >= 3:
                dataset = path_parts[0]
                task = path_parts[1]
                filename = path_parts[2]
                
                # Extract data format from filename
                data_format = None
                for fmt in data_formats:
                    if f"_{fmt}_converted_prompts.csv" in filename:
                        data_format = fmt
                        break
                
                if data_format:
                    datasets.add(dataset)
                    tasks.add(task)
                    
                    # Read the CSV file
                    print(f"Processing: {dataset}/{task}/{data_format}")
                    
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        total_count = 0
                        correct_count = 0
                        
                        for row in reader:
                            total_count += 1
                            if 'Correct' in row:
                                # Handle different representations of True/False
                                correct_val = row['Correct'].strip().lower()
                                if correct_val in ['true', '1', 'yes']:
                                    correct_count += 1
                            else:
                                print(f"Warning: 'Correct' column not found in {csv_file}")
                                break
                        
                        # Store results
                        key = (dataset, task, data_format)
                        results[key] = {
                            'correct': correct_count,
                            'total': total_count,
                            'percentage': (correct_count / total_count * 100) if total_count > 0 else 0
                        }
                        
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            continue
    
    # Convert to sorted lists for consistent ordering
    datasets = sorted(list(datasets))
    tasks = sorted(list(tasks))
    data_formats = sorted(data_formats)
    
    print(f"\nFound datasets: {datasets}")
    print(f"Found tasks: {tasks}")
    print(f"Found data formats: {data_formats}")
    
    return datasets, tasks, data_formats, results

def create_tables(datasets, tasks, data_formats, results):
    """
    Create count and percentage tables from the results.
    
    Args:
        datasets, tasks, data_formats: Lists of dataset, task, and format names
        results: Dictionary with analysis results
        
    Returns:
        tuple: (count_table, percentage_table) as lists of lists
    """
    
    # Initialize result tables with tasks as columns (aggregated across all datasets)
    count_table = []
    percentage_table = []
    
    # Build tables with data formats as rows and tasks as columns
    for data_format in data_formats:
        count_row = []
        percentage_row = []
        
        for task in tasks:
            # Aggregate results across all datasets for this task and format
            total_correct = 0
            total_questions = 0
            
            for dataset in datasets:
                key = (dataset, task, data_format)
                if key in results:
                    total_correct += results[key]['correct']
                    total_questions += results[key]['total']
            
            if total_questions > 0:
                count_row.append(f"{total_correct}/{total_questions}")
                percentage = (total_correct / total_questions * 100)
                percentage_row.append(f"{percentage:.1f}%")
            else:
                count_row.append("N/A")
                percentage_row.append("N/A")
        
        count_table.append(count_row)
        percentage_table.append(percentage_row)
    
    return count_table, percentage_table, tasks

def print_table(table, row_headers, col_headers, title):
    """
    Print a formatted table.
    
    Args:
        table: List of lists representing the table data
        row_headers: List of row header names
        col_headers: List of column header names
        title: Title for the table
    """
    
    print("\n" + "="*120)
    print(f"{title}")
    print("="*120)
    
    # Calculate column widths
    col_widths = [max(len(str(col)), max(len(str(row[i])) for row in table)) + 2 
                  for i, col in enumerate(col_headers)]
    row_header_width = max(len(str(header)) for header in row_headers) + 2
    
    # Print header row
    print(f"{'Format':<{row_header_width}}", end="")
    for i, header in enumerate(col_headers):
        print(f"{header:<{col_widths[i]}}", end="")
    print()
    
    # Print separator
    print("-" * (row_header_width + sum(col_widths)))
    
    # Print data rows
    for i, row in enumerate(table):
        print(f"{row_headers[i]:<{row_header_width}}", end="")
        for j, cell in enumerate(row):
            print(f"{cell:<{col_widths[j]}}", end="")
        print()

def save_results(count_table, percentage_table, row_headers, col_headers, output_dir):
    """
    Save the analysis results to CSV files.
    
    Args:
        count_table, percentage_table: Table data as lists of lists
        row_headers, col_headers: Headers for rows and columns
        output_dir: Directory to save output files
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save count table
    count_file = os.path.join(output_dir, "benchmark_results_counts.csv")
    with open(count_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Format'] + col_headers)
        for i, row in enumerate(count_table):
            writer.writerow([row_headers[i]] + row)
    
    # Save percentage table
    percentage_file = os.path.join(output_dir, "benchmark_results_percentages.csv")
    with open(percentage_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Format'] + col_headers)
        for i, row in enumerate(percentage_table):
            writer.writerow([row_headers[i]] + row)
    
    print(f"\nResults saved to:")
    print(f"- Count table: {count_file}")
    print(f"- Percentage table: {percentage_file}")

def generate_summary_statistics(results):
    """
    Generate additional summary statistics.
    
    Args:
        results (dict): Results dictionary from analysis
    """
    
    print("\n" + "="*100)
    print("SUMMARY STATISTICS")
    print("="*100)
    
    # Overall statistics
    total_questions = sum(r['total'] for r in results.values())
    total_correct = sum(r['correct'] for r in results.values())
    overall_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    print(f"Overall Results: {total_correct}/{total_questions} ({overall_percentage:.1f}%)")
    
    # Statistics by data format
    format_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for (dataset, task, data_format), result in results.items():
        format_stats[data_format]['correct'] += result['correct']
        format_stats[data_format]['total'] += result['total']
    
    print(f"\nResults by Data Format:")
    for data_format in sorted(format_stats.keys()):
        stats = format_stats[data_format]
        pct = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {data_format.upper()}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")
    
    # Statistics by task
    task_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for (dataset, task, data_format), result in results.items():
        task_stats[task]['correct'] += result['correct']
        task_stats[task]['total'] += result['total']
    
    print(f"\nResults by Task:")
    for task in sorted(task_stats.keys()):
        stats = task_stats[task]
        pct = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {task}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")
    
    # Statistics by dataset
    dataset_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for (dataset, task, data_format), result in results.items():
        dataset_stats[dataset]['correct'] += result['correct']
        dataset_stats[dataset]['total'] += result['total']
    
    print(f"\nResults by Dataset:")
    for dataset in sorted(dataset_stats.keys()):
        stats = dataset_stats[dataset]
        pct = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {dataset}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")

def main():
    """Main function to run the analysis."""
    
    # Set the base path for benchmark results
    base_path = "/insight-fast/dnguyen/Q_Benchmark/benchmark_results/gpt-4.1-mini"
    output_dir = "/insight-fast/dnguyen/Q_Benchmark/analysis_results"
    
    print("Starting benchmark results analysis...")
    print(f"Base path: {base_path}")
    
    # Check if base path exists
    if not os.path.exists(base_path):
        print(f"Error: Base path does not exist: {base_path}")
        return
    
    # Run the analysis
    datasets, tasks, data_formats, results = analyze_benchmark_results(base_path)
    
    # Create tables
    count_table, percentage_table, task_columns = create_tables(datasets, tasks, data_formats, results)
    
    # Display tables
    print_table(count_table, data_formats, task_columns, "TABLE 1: CORRECT ANSWERS / TOTAL ANSWERS")
    print_table(percentage_table, data_formats, task_columns, "TABLE 2: PERCENTAGE CORRECT")
    
    # Save results
    save_results(count_table, percentage_table, data_formats, task_columns, output_dir)
    
    # Generate summary statistics
    generate_summary_statistics(results)
    
    print(f"\nAnalysis complete! Check the output directory: {output_dir}")

if __name__ == "__main__":
    main()