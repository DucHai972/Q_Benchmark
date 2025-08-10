#!/usr/bin/env python3
"""
Benchmark Results Analysis Script

This script analyzes the benchmark results from Q_Benchmark/benchmark_results/
and generates two tables:
1. Table showing correct/total counts for each data format and task combination
2. Table showing percentage correct for each data format and task combination

The script processes all CSV files in the benchmark results directory structure.

Usage:
  python benchmark_analysis.py                                    # Standard analysis
  python benchmark_analysis.py --variants all                     # All variants analysis
  python benchmark_analysis.py --variants wo_role_prompting       # Specific variant
  python benchmark_analysis.py --model gpt-4.1-mini              # Specific model
"""

import os
import csv
import glob
import argparse
from pathlib import Path
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

def save_results(count_table, percentage_table, row_headers, col_headers, output_dir, results=None):
    """
    Save the analysis results to CSV files.
    
    Args:
        count_table, percentage_table: Table data as lists of lists
        row_headers, col_headers: Headers for rows and columns
        output_dir: Directory to save output files
        results: Optional results dictionary for dataset summary
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
    
    # Save dataset summary table (average across all tasks per dataset)
    dataset_file = os.path.join(output_dir, "dataset_summary.csv")
    if results:
        save_dataset_summary(results, dataset_file)
        print(f"\nResults saved to:")
        print(f"- Count table: {count_file}")
        print(f"- Percentage table: {percentage_file}")
        print(f"- Dataset summary: {dataset_file}")
    else:
        print(f"\nResults saved to:")
        print(f"- Count table: {count_file}")
        print(f"- Percentage table: {percentage_file}")

def save_dataset_summary(results, dataset_file):
    """
    Save dataset-level summary (average across all tasks in each dataset).
    
    Args:
        results (dict): Results dictionary from analysis
        dataset_file (str): Path to save the dataset summary CSV
    """
    
    # Calculate dataset-level statistics
    dataset_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    # Aggregate results by dataset
    for (dataset, task, data_format), result in results.items():
        dataset_stats[dataset]['correct'] += result['correct']
        dataset_stats[dataset]['total'] += result['total']
    
    # Write to CSV
    with open(dataset_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Dataset', 'Correct_Answers', 'Total_Questions', 'Average_Accuracy_Percent'])
        
        for dataset in sorted(dataset_stats.keys()):
            stats = dataset_stats[dataset]
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            writer.writerow([
                dataset, 
                stats['correct'], 
                stats['total'], 
                f"{accuracy:.1f}%"
            ])

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

def get_available_variants():
    """Get list of available prompt variants."""
    variants_dir = Path("/insight-fast/dnguyen/Q_Benchmark/converted_prompts_variants")
    if variants_dir.exists():
        return sorted([d.name for d in variants_dir.iterdir() if d.is_dir()])
    return []

def get_available_models():
    """Get list of available model result directories."""
    results_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_results")
    if results_dir.exists():
        return sorted([d.name for d in results_dir.iterdir() if d.is_dir()])
    return []

def analyze_single_variant(model, variant, base_results_dir, output_base_dir):
    """Analyze a single variant and save results."""
    if variant:
        model_dir_name = f"{model}_{variant}"
        output_suffix = f"_{variant}"
        analysis_type = f"{model} with variant '{variant}'"
    else:
        model_dir_name = model
        output_suffix = ""
        analysis_type = f"{model} (standard)"
    
    base_path = base_results_dir / model_dir_name
    output_dir = output_base_dir / f"{model_dir_name}"
    
    print(f"\n{'='*60}")
    print(f"ANALYZING: {analysis_type}")
    print(f"{'='*60}")
    print(f"Base path: {base_path}")
    print(f"Output dir: {output_dir}")
    
    # Check if base path exists
    if not base_path.exists():
        print(f"Warning: Base path does not exist: {base_path}")
        return False
    
    # Run the analysis
    datasets, tasks, data_formats, results = analyze_benchmark_results(str(base_path))
    
    if not results:
        print(f"No results found for {analysis_type}")
        return False
    
    # Create tables
    count_table, percentage_table, task_columns = create_tables(datasets, tasks, data_formats, results)
    
    # Display tables
    print_table(count_table, data_formats, task_columns, 
                f"TABLE 1: CORRECT ANSWERS / TOTAL ANSWERS - {analysis_type}")
    print_table(percentage_table, data_formats, task_columns, 
                f"TABLE 2: PERCENTAGE CORRECT - {analysis_type}")
    
    # Save results
    save_results(count_table, percentage_table, data_formats, task_columns, str(output_dir), results)
    
    # Generate summary statistics
    generate_summary_statistics(results)
    
    print(f"\nAnalysis complete for {analysis_type}!")
    return True

def main():
    """Main function to run the analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze Q-Benchmark results across different prompt variants and models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_analysis.py                                    # Analyze gpt-4.1-mini standard
  python benchmark_analysis.py --variants all                     # All variants for gpt-4.1-mini
  python benchmark_analysis.py --variants wo_role_prompting       # Specific variant for gpt-4.1-mini
  python benchmark_analysis.py --model gemini-2.5-flash          # Different model, standard
  python benchmark_analysis.py --model gpt-4.1-mini --variants all  # All variants for specific model
        """
    )
    
    # Get available options
    available_variants = get_available_variants()
    available_models = get_available_models()
    
    parser.add_argument("--variants", 
                       choices=["all"] + available_variants,
                       help="Prompt variant to analyze. 'all' analyzes all available variants.")
    
    parser.add_argument("--model", 
                       choices=available_models,
                       default="gpt-4.1-mini",
                       help="Model to analyze (default: gpt-4.1-mini)")
    
    parser.add_argument("--output-dir",
                       default="/insight-fast/dnguyen/Q_Benchmark/analysis_results",
                       help="Base output directory for results")
    
    parser.add_argument("--list", action="store_true",
                       help="List available variants and models")
    
    args = parser.parse_args()
    
    # Handle list option
    if args.list:
        print("Available models:")
        for model in available_models:
            print(f"  - {model}")
        print("\nAvailable variants:")
        for variant in available_variants:
            print(f"  - {variant}")
        return
    
    base_results_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_results")
    output_base_dir = Path(args.output_dir)
    
    print("Starting Q-Benchmark results analysis...")
    print(f"Model: {args.model}")
    print(f"Variants: {args.variants or 'standard (no variants)'}")
    
    success_count = 0
    total_analyses = 0
    
    if args.variants == "all":
        # Analyze standard version first
        total_analyses += 1
        if analyze_single_variant(args.model, None, base_results_dir, output_base_dir):
            success_count += 1
        
        # Then analyze all variants
        for variant in available_variants:
            total_analyses += 1
            if analyze_single_variant(args.model, variant, base_results_dir, output_base_dir):
                success_count += 1
                
    elif args.variants:
        # Analyze specific variant
        total_analyses += 1
        if analyze_single_variant(args.model, args.variants, base_results_dir, output_base_dir):
            success_count += 1
            
    else:
        # Analyze standard version only
        total_analyses += 1
        if analyze_single_variant(args.model, None, base_results_dir, output_base_dir):
            success_count += 1
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"ANALYSIS SUMMARY")
    print(f"{'='*80}")
    print(f"Completed analyses: {success_count}/{total_analyses}")
    print(f"Output directory: {output_base_dir}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()