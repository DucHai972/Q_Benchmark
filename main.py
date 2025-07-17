#!/usr/bin/env python3
"""
Q-Benchmark CLI - A friendly command-line interface for running LLM benchmarks
"""

import argparse
import sys
import os
from pathlib import Path
from benchmark_pipeline import BenchmarkPipeline
from tqdm import tqdm


def get_available_datasets():
    """Get list of available datasets from preprocessed_data directory"""
    datasets = []
    data_dir = Path("preprocessed_data")
    if data_dir.exists():
        datasets = [d.name for d in data_dir.iterdir() if d.is_dir()]
    return sorted(datasets)


def get_available_tasks():
    """Get list of available benchmark tasks"""
    return [
        "answer_lookup",
        "answer_reverse_lookup", 
        "conceptual_aggregation",
        "multi_hop_relational_inference",
        "respondent_count",
        "rule_based_querying"
    ]


def get_available_formats():
    """Get list of available data formats"""
    return ["json", "xml", "html", "md", "txt", "ttl"]


def get_available_models():
    """Get list of available LLM models"""
    return ["openai", "google", "deepseek"]


def print_available_options():
    """Print all available options for user reference"""
    print("\n📊 Available Options:")
    print("=" * 50)
    
    print(f"🗂️  Datasets: {', '.join(get_available_datasets())}")
    print(f"🎯 Tasks: {', '.join(get_available_tasks())}")
    print(f"📋 Formats: {', '.join(get_available_formats())}")
    print(f"🤖 Models: {', '.join(get_available_models())}")
    print()


def validate_args(args):
    """Validate command line arguments"""
    errors = []
    
    # Validate datasets
    available_datasets = get_available_datasets()
    for dataset in args.datasets:
        if dataset not in available_datasets:
            errors.append(f"Dataset '{dataset}' not found. Available: {available_datasets}")
    
    # Validate tasks
    available_tasks = get_available_tasks()
    for task in args.tasks:
        if task not in available_tasks:
            errors.append(f"Task '{task}' not found. Available: {available_tasks}")
    
    # Validate formats
    available_formats = get_available_formats()
    for fmt in args.formats:
        if fmt not in available_formats:
            errors.append(f"Format '{fmt}' not found. Available: {available_formats}")
    
    # Validate models
    available_models = get_available_models()
    for model in args.models:
        if model not in available_models and model != "all":
            errors.append(f"Model '{model}' not found. Available: {available_models}")
    
    # Validate cases
    if args.cases <= 0:
        errors.append("Number of cases must be positive")
    
    return errors


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="🚀 Q-Benchmark: Evaluate LLMs across different data formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run quick test with 5 cases on healthcare dataset
  python main.py --dataset healthcare-dataset --cases 5
  
  # Test specific model with more cases
  python main.py --model openai --formats json xml --cases 10
  
  # Full benchmark on all datasets and tasks
  python main.py --datasets all --tasks all --cases 20
  
  # Test specific model and task with custom output
  python main.py --model deepseek --task answer_lookup --output my_results --cases 15
        """
    )
    
    # Dataset selection
    parser.add_argument(
        "--dataset", "--datasets", 
        nargs="+", 
        dest="datasets",
        default=["healthcare-dataset"],
        help="Dataset(s) to benchmark (default: healthcare-dataset). Use 'all' for all datasets"
    )
    
    # Task selection
    parser.add_argument(
        "--task", "--tasks",
        nargs="+",
        dest="tasks", 
        default=["answer_lookup"],
        help="Task(s) to run (default: answer_lookup). Use 'all' for all tasks"
    )
    
    # Model selection
    parser.add_argument(
        "--model", "--models",
        nargs="+",
        dest="models",
        default=["all"],
        help="LLM model(s) to test: openai, google, deepseek, or 'all' (default: all)"
    )
    
    # Format selection
    parser.add_argument(
        "--format", "--formats",
        nargs="+", 
        dest="formats",
        default=["json", "xml"],
        help="Data format(s) to test (default: json xml)"
    )
    
    # Number of cases
    parser.add_argument(
        "--cases", "-n",
        type=int,
        default=5,
        help="Number of test cases per task/format combination (default: 5)"
    )
    
    # Output directory
    parser.add_argument(
        "--output", "-o",
        default="",
        help="Output directory name inside benchmark_results/ (default: auto-generated with timestamp)"
    )
    
    # Verbose output
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # List available options
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available datasets, tasks, formats, and models"
    )
    
    # Generate Excel report
    parser.add_argument(
        "--excel", "-e",
        action="store_true", 
        default=True,
        help="Generate Excel summary table (default: True)"
    )
    
    # Skip Excel report
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel summary table generation"
    )
    
    return parser


def expand_special_values(args):
    """Expand 'all' values to actual lists"""
    if "all" in args.datasets:
        args.datasets = get_available_datasets()
    
    if "all" in args.tasks:
        args.tasks = get_available_tasks()
    
    if "all" in args.models:
        args.models = get_available_models()
    
    if "all" in args.formats:
        args.formats = get_available_formats()
    
    # Handle no-excel flag
    if args.no_excel:
        args.excel = False
    
    return args


def print_config(args):
    """Print benchmark configuration"""
    print("\n🎯 Benchmark Configuration:")
    print("=" * 50)
    print(f"📊 Datasets: {', '.join(args.datasets)}")
    print(f"🎯 Tasks: {', '.join(args.tasks)}")
    print(f"🤖 Models: {', '.join(args.models)}")
    print(f"📋 Formats: {', '.join(args.formats)}")
    print(f"📈 Cases per combination: {args.cases}")
    
    # Show proper output directory path
    if args.output:
        output_path = f"benchmark_results/{args.output}"
    else:
        output_path = "benchmark_results/ (with auto-generated timestamp)"
    print(f"📁 Output directory: {output_path}")
    print(f"📊 Generate Excel: {args.excel}")
    print()


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        print_available_options()
        return
    
    # Expand special values
    args = expand_special_values(args)
    
    # Validate arguments
    errors = validate_args(args)
    if errors:
        print("❌ Validation Errors:")
        for error in errors:
            print(f"   • {error}")
        print("\nUse --list to see available options")
        sys.exit(1)
    
    # Check environment file
    if not os.path.exists(".env"):
        print("❌ Error: .env file not found!")
        print("Please create a .env file with your API keys:")
        print("   OPENAI_API_KEY=your_key_here")
        print("   GOOGLE_API_KEY=your_key_here") 
        print("   DEEPSEEK_API_KEY=your_key_here")
        sys.exit(1)
    
    # Print configuration
    print("🚀 Starting Q-Benchmark...")
    print_config(args)
    
    try:
        # Prepare output directory inside benchmark_results/
        if args.output:
            # User specified a custom output name
            output_dir = Path("benchmark_results") / args.output
        else:
            # Use default benchmark_results directory (pipeline will add timestamp)
            output_dir = Path("benchmark_results")
        
        # Create a single timestamped run directory for all combinations
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        single_run_dir = output_dir / f"run_{timestamp}"
        single_run_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipeline with selected models and the fixed run directory
        pipeline = BenchmarkPipeline(output_dir=str(output_dir), selected_models=args.models)
        
        # Calculate total evaluations for progress bar
        total_evaluations = len(args.datasets) * len(args.tasks) * len(args.models) * len(args.formats) * args.cases
        all_result_dirs = []
        print(f"\n🔄 Running benchmark with {total_evaluations} total evaluations...")
        with tqdm(total=total_evaluations, desc="🚀 Q-Benchmark", unit="eval") as pbar:
            for dataset in args.datasets:
                for task in args.tasks:
                    pbar.set_description(f"📊 {dataset} → {task}")
                    result_dir = pipeline.run_benchmark_fixed_dir(
                        run_dir=str(single_run_dir),
                        dataset=dataset,
                        task=task,
                        max_cases=args.cases,
                        formats=args.formats,
                        progress_bar=pbar
                    )
                    all_result_dirs.append(result_dir)
        
        # Generate overall summary and Excel tables after all combinations are complete
        if args.excel:
            print("\n📊 Generating Excel reports and summary...")
            pipeline._generate_simple_summary(single_run_dir)
            pipeline._generate_excel_table(single_run_dir)
            pipeline._generate_score_excel_table(single_run_dir)
        
        print(f"\n✅ Benchmark completed successfully!")
        
        # Show actual output directory path
        if all_result_dirs:
            actual_output = Path(all_result_dirs[-1]).parent
            print(f"📁 Results saved to: {actual_output}")
        else:
            if args.output:
                print(f"📁 Results saved to: benchmark_results/{args.output}")
            else:
                print(f"📁 Results saved to: benchmark_results/")
        
        if args.excel:
            # Check for Excel files in the latest result directory
            if all_result_dirs:
                latest_dir = Path(all_result_dirs[-1])
                excel_file = latest_dir / "benchmark_results_table.xlsx"
                if excel_file.exists():
                    print(f"📊 Excel report: {excel_file}")
        
        # Print quick summary
        total_evaluations = len(args.datasets) * len(args.tasks) * args.cases * len(args.formats)
        print(f"🎯 Evaluated {total_evaluations} test cases across {len(args.datasets) * len(args.tasks)} dataset/task combinations")
        print(f"📈 Results multiplied by number of available LLM models")
        
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 