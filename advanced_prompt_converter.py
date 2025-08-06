#!/usr/bin/env python3
"""
Advanced Prompt Converter for Q-Benchmark

This script converts advanced prompts by combining:
1. Advanced prompt templates from advanced_prompts/ directory
2. Questionnaire data from benchmark_cache/ directory

Output format matches the existing converted_prompts/ structure with CSV files
containing: case_id, task, question, questionnaire, expected_answer, prompt, Response, Correct
"""

import json
import csv
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys


class AdvancedPromptConverter:
    def __init__(self, advanced_prompts_dir: str = "advanced_prompts", 
                 benchmark_cache_dir: str = "benchmark_cache",
                 output_dir: str = "converted_prompts"):
        self.advanced_prompts_dir = Path(advanced_prompts_dir)
        self.benchmark_cache_dir = Path(benchmark_cache_dir) 
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported data formats
        self.formats = ["json", "xml", "html", "md", "txt", "ttl"]
        
    def load_advanced_prompt_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load and parse an advanced prompt JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return [data]
        except Exception as e:
            print(f"Error loading advanced prompt file {filepath}: {e}")
            return []
    
    def load_questionnaire_data(self, filepath: Path) -> str:
        """Load questionnaire data from benchmark cache file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading questionnaire file {filepath}: {e}")
            return ""
    
    def substitute_prompt_variables(self, prompt_template: str, variables: Dict[str, str]) -> str:
        """Substitute variables in prompt template with actual values"""
        result = prompt_template
        
        # Replace bracketed variables with their values
        for key, value in variables.items():
            placeholder = f"[{key}]"
            if placeholder in result:
                result = result.replace(placeholder, value)
        
        return result
    
    def load_case1_data(self, dataset: str, task: str, format_type: str) -> str:
        """Load case_1 data to use as example in CASE_1"""
        case1_file = (self.benchmark_cache_dir / dataset / task / 
                     format_type / f"case_1.{format_type}")
        
        if case1_file.exists():
            return self.load_questionnaire_data(case1_file)
        return ""
    
    def generate_converted_prompt(self, advanced_prompt: Dict[str, Any], 
                                  questionnaire_data: str, format_type: str,
                                  dataset: str, task: str) -> Dict[str, str]:
        """Generate a converted prompt entry"""
        
        # Extract components from advanced prompt
        case_id = advanced_prompt.get("case_id", "")
        task_name = advanced_prompt.get("task", "")
        question = advanced_prompt.get("question", "")
        expected_answer = advanced_prompt.get("expected_answer", "")
        prompt_template = advanced_prompt.get("prompt", "")
        metadata = advanced_prompt.get("metadata", {})
        
        # Load case_1 data for CASE_1 example
        case1_data = self.load_case1_data(dataset, task, format_type)
        
        # Process CASE_1 to replace placeholder with actual case_1 data
        case_1_template = advanced_prompt.get("CASE_1", "")
        case_1_with_data = case_1_template.replace("[Insert the full data block here]", case1_data)
        
        # Prepare variables for substitution
        variables = {
            "questionnaire": questionnaire_data,
            "question": question,
            "ROLE_PROMPTING": advanced_prompt.get("ROLE_PROMPTING", ""),
            "FORMAT_EXPLANATION": advanced_prompt.get("FORMAT_EXPLANATION", ""),
            "OUTPUT_INSTRUCTIONS": advanced_prompt.get("OUTPUT_INSTRUCTIONS", ""),
            "CASE_1": case_1_with_data
        }
        
        # Generate the final prompt
        final_prompt = self.substitute_prompt_variables(prompt_template, variables)
        
        return {
            "case_id": case_id,
            "task": task_name,
            "question": question,
            "questionnaire": questionnaire_data,
            "expected_answer": expected_answer,
            "prompt": final_prompt,
            "Response": "",
            "Correct": ""
        }
    
    def process_dataset_task_format(self, dataset: str, task: str, format_type: str) -> bool:
        """Process a specific dataset/task/format combination"""
        
        # Load advanced prompt file
        advanced_prompt_file = (self.advanced_prompts_dir / dataset / 
                               f"{dataset}_{task}_qa_pairs.json")
        
        if not advanced_prompt_file.exists():
            print(f"Advanced prompt file not found: {advanced_prompt_file}")
            return False
            
        advanced_prompts = self.load_advanced_prompt_file(advanced_prompt_file)
        if not advanced_prompts:
            print(f"No advanced prompts loaded from {advanced_prompt_file}")
            return False
        
        # Prepare output data
        converted_prompts = []
        
        # Process each advanced prompt case
        for advanced_prompt in advanced_prompts:
            case_id = advanced_prompt.get("case_id", "")
            
            # Load corresponding questionnaire data
            questionnaire_file = (self.benchmark_cache_dir / dataset / task / 
                                format_type / f"{case_id}.{format_type}")
            
            if not questionnaire_file.exists():
                print(f"Warning: Questionnaire file not found: {questionnaire_file}")
                continue
                
            questionnaire_data = self.load_questionnaire_data(questionnaire_file)
            if not questionnaire_data:
                print(f"Warning: No questionnaire data loaded from {questionnaire_file}")
                continue
            
            # Generate converted prompt
            converted_prompt = self.generate_converted_prompt(
                advanced_prompt, questionnaire_data, format_type, dataset, task)
            converted_prompts.append(converted_prompt)
        
        if not converted_prompts:
            print(f"No converted prompts generated for {dataset}/{task}/{format_type}")
            return False
        
        # Write output CSV file with smart handling
        output_file = (self.output_dir / dataset / task / 
                      f"{task}_{format_type}_converted_prompts.csv")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load existing CSV data if file exists
            existing_data = {}
            if output_file.exists():
                with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        existing_data[row['case_id']] = row
            
            # Update existing data with new prompts (overwrite or add)
            for prompt in converted_prompts:
                case_id = prompt['case_id']
                if case_id in existing_data:
                    print(f"Overwriting existing case_id: {case_id}")
                else:
                    print(f"Adding new case_id: {case_id}")
                existing_data[case_id] = prompt
            
            # Sort by case_id (natural sorting for case_1, case_2, etc.)
            def natural_sort_key(case_id):
                # Extract number from case_id (e.g., "case_1" -> 1)
                try:
                    if case_id.startswith('case_'):
                        return int(case_id.split('_')[1])
                    else:
                        return float('inf')  # Put non-standard case_ids at the end
                except (ValueError, IndexError):
                    return float('inf')
            
            sorted_prompts = sorted(existing_data.values(), key=lambda x: natural_sort_key(x['case_id']))
            
            # Write the updated and sorted CSV file
            fieldnames = ["case_id", "task", "question", "questionnaire", 
                        "expected_answer", "prompt", "Response", "Correct"]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for prompt in sorted_prompts:
                    writer.writerow(prompt)
            
            print(f"Successfully updated: {output_file} ({len(sorted_prompts)} total prompts, {len(converted_prompts)} processed)")
            return True
            
        except Exception as e:
            print(f"Error writing output file {output_file}: {e}")
            return False
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets"""
        if not self.advanced_prompts_dir.exists():
            return []
        return [d.name for d in self.advanced_prompts_dir.iterdir() if d.is_dir()]
    
    def get_available_tasks(self, dataset: str) -> List[str]:
        """Get list of available tasks for a dataset"""
        dataset_dir = self.advanced_prompts_dir / dataset
        if not dataset_dir.exists():
            return []
        
        tasks = set()
        for file in dataset_dir.glob("*.json"):
            # Extract task from filename: dataset_task_qa_pairs.json
            name_parts = file.stem.split('_')
            if len(name_parts) >= 3 and name_parts[-2] == "qa" and name_parts[-1] == "pairs":
                task = "_".join(name_parts[1:-2])  # Remove dataset prefix and qa_pairs suffix
                tasks.add(task)
        
        return sorted(list(tasks))
    
    def convert_all(self, datasets: Optional[List[str]] = None, 
                   tasks: Optional[List[str]] = None,
                   formats: Optional[List[str]] = None) -> bool:
        """Convert all specified datasets/tasks/formats"""
        
        # Use all available if not specified
        if datasets is None:
            datasets = self.get_available_datasets()
        if formats is None:
            formats = self.formats
            
        success_count = 0
        total_count = 0
        
        for dataset in datasets:
            dataset_tasks = tasks if tasks else self.get_available_tasks(dataset)
            
            for task in dataset_tasks:
                for format_type in formats:
                    total_count += 1
                    if self.process_dataset_task_format(dataset, task, format_type):
                        success_count += 1
        
        print(f"\nConversion completed: {success_count}/{total_count} successful")
        return success_count == total_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert advanced prompts by combining templates with questionnaire data")
    
    parser.add_argument("--datasets", nargs="*", 
                       help="Dataset names to process (default: all)")
    parser.add_argument("--tasks", nargs="*",
                       help="Task names to process (default: all)")
    parser.add_argument("--formats", nargs="*", 
                       choices=["json", "xml", "html", "md", "txt", "ttl"],
                       help="Data formats to process (default: all)")
    parser.add_argument("--advanced-prompts-dir", default="advanced_prompts",
                       help="Directory containing advanced prompt templates")
    parser.add_argument("--benchmark-cache-dir", default="benchmark_cache", 
                       help="Directory containing questionnaire data")
    parser.add_argument("--output-dir", default="converted_prompts",
                       help="Output directory for converted prompts")
    parser.add_argument("--list", action="store_true",
                       help="List available datasets and tasks")
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = AdvancedPromptConverter(
        args.advanced_prompts_dir,
        args.benchmark_cache_dir, 
        args.output_dir
    )
    
    # List available options
    if args.list:
        print("Available datasets:")
        for dataset in converter.get_available_datasets():
            print(f"  - {dataset}")
            tasks = converter.get_available_tasks(dataset)
            if tasks:
                print(f"    Tasks: {', '.join(tasks)}")
        print(f"\nAvailable formats: {', '.join(converter.formats)}")
        return
    
    # Convert prompts
    success = converter.convert_all(
        datasets=args.datasets,
        tasks=args.tasks,
        formats=args.formats
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()