#!/usr/bin/env python3
"""
Advanced Prompt Converter

This script reads advanced prompt templates from the advanced_prompts directory
and converts them into actual LLM prompts by replacing all placeholders with 
actual data from the preprocessed_data directory.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedPromptConverter:
    """Converts advanced prompt templates into actual LLM prompts."""
    
    def __init__(self, 
                 advanced_prompts_dir: str = "advanced_prompts",
                 preprocessed_data_dir: str = "preprocessed_data",
                 output_dir: str = "converted_prompts"):
        """
        Initialize the prompt converter.
        
        Args:
            advanced_prompts_dir: Directory containing advanced prompt templates
            preprocessed_data_dir: Directory containing preprocessed data
            output_dir: Directory to save converted prompts
        """
        self.advanced_prompts_dir = Path(advanced_prompts_dir)
        self.preprocessed_data_dir = Path(preprocessed_data_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
    def load_questionnaire_data(self, dataset: str, format: str = "json") -> str:
        """
        Load questionnaire data for a dataset in specified format.
        
        Args:
            dataset: Dataset name
            format: Data format (json, xml, html, md, txt, ttl)
            
        Returns:
            String representation of the questionnaire data
        """
        # Map format extensions
        format_extensions = {
            "json": ".json",
            "xml": ".xml", 
            "html": ".html",
            "md": ".md",
            "txt": ".txt",
            "ttl": ".ttl"
        }
        
        if format not in format_extensions:
            raise ValueError(f"Unsupported format: {format}")
        
        # Find the questionnaire file for this dataset
        dataset_dir = self.preprocessed_data_dir / dataset
        if not dataset_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
        
        # Look for questionnaire files
        questionnaire_files = list(dataset_dir.glob(f"*questionnaire{format_extensions[format]}"))
        if not questionnaire_files:
            raise FileNotFoundError(f"No questionnaire file found for {dataset} in {format} format")
        
        questionnaire_file = questionnaire_files[0]
        
        with open(questionnaire_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def replace_data_placeholders(self, text: str, dataset: str, format: str = "json") -> str:
        """
        Replace data placeholders like '[Insert the full data block here]' with actual data.
        
        Args:
            text: Text containing placeholders
            dataset: Dataset name
            format: Data format
            
        Returns:
            Text with placeholders replaced
        """
        if "[Insert the full data block here]" in text:
            questionnaire_data = self.load_questionnaire_data(dataset, format)
            text = text.replace("[Insert the full data block here]", questionnaire_data)
        
        return text
    
    def convert_prompt_template(self, prompt_data: Dict[str, Any], dataset: str, format: str = "json") -> str:
        """
        Convert a single prompt template into an actual LLM prompt.
        
        Args:
            prompt_data: Dictionary containing prompt template data
            dataset: Dataset name
            format: Data format
            
        Returns:
            Final LLM prompt string
        """
        # Get the template
        template = prompt_data.get("prompt", "")
        
        if not template:
            logger.warning(f"No prompt template found for case {prompt_data.get('case_id', 'unknown')}")
            return ""
        
        # Create a copy of prompt_data for replacements
        replacement_data = prompt_data.copy()
        
        # Replace data placeholders in all relevant fields
        fields_with_data_placeholders = ["CASE_1", "questionnaire"]
        for field in fields_with_data_placeholders:
            if field in replacement_data:
                replacement_data[field] = self.replace_data_placeholders(
                    replacement_data[field], dataset, format
                )
        
        # Replace template placeholders with actual values
        final_prompt = template
        
        # List of placeholder patterns to replace
        placeholder_patterns = [
            "[CASE_1]",
            "[questionnaire]", 
            "[ROLE_PROMPTING]",
            "[FORMAT_EXPLANATION]",
            "[OUTPUT_INSTRUCTIONS]",
            "[question]"
        ]
        
        for pattern in placeholder_patterns:
            # Remove brackets to get the key name
            key = pattern[1:-1]  # Remove [ and ]
            
            if key in replacement_data:
                final_prompt = final_prompt.replace(pattern, str(replacement_data[key]))
            else:
                logger.warning(f"Placeholder {pattern} found but no corresponding key '{key}' in prompt data")
        
        return final_prompt
    
    def convert_dataset_prompts(self, dataset: str, task: Optional[str] = None, 
                               format: str = "json", max_cases: Optional[int] = None) -> Dict[str, Any]:
        """
        Convert all prompts for a dataset/task combination.
        
        Args:
            dataset: Dataset name
            task: Task name (if None, convert all tasks)
            format: Data format
            max_cases: Maximum number of cases to convert
            
        Returns:
            Dictionary containing converted prompts
        """
        results = {
            "dataset": dataset,
            "task": task,
            "format": format,
            "converted_prompts": []
        }
        
        # Find advanced prompt files for this dataset
        dataset_prompts_dir = self.advanced_prompts_dir / dataset
        if not dataset_prompts_dir.exists():
            raise FileNotFoundError(f"Advanced prompts directory not found: {dataset_prompts_dir}")
        
        # Get prompt files
        if task:
            prompt_files = list(dataset_prompts_dir.glob(f"*{task}*qa_pairs.json"))
        else:
            prompt_files = list(dataset_prompts_dir.glob("*qa_pairs.json"))
        
        if not prompt_files:
            raise FileNotFoundError(f"No prompt files found for dataset {dataset}" + 
                                   (f" task {task}" if task else ""))
        
        for prompt_file in prompt_files:
            logger.info(f"Converting prompts from: {prompt_file}")
            
            # Load prompt data
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data_list = json.load(f)
            
            # Convert each prompt
            converted_count = 0
            for prompt_data in prompt_data_list:
                if max_cases and converted_count >= max_cases:
                    break
                
                try:
                    converted_prompt = self.convert_prompt_template(prompt_data, dataset, format)
                    
                    result_item = {
                        "case_id": prompt_data.get("case_id", f"case_{converted_count + 1}"),
                        "task": prompt_data.get("task", "unknown"),
                        "question": prompt_data.get("question", ""),
                        "expected_answer": prompt_data.get("expected_answer", ""),
                        "converted_prompt": converted_prompt,
                        "metadata": prompt_data.get("metadata", {})
                    }
                    
                    results["converted_prompts"].append(result_item)
                    converted_count += 1
                    
                except Exception as e:
                    logger.error(f"Error converting prompt for case {prompt_data.get('case_id', 'unknown')}: {e}")
        
        logger.info(f"Converted {len(results['converted_prompts'])} prompts for {dataset}")
        return results
    
    def save_converted_prompts(self, results: Dict[str, Any], filename: str, output_format: str = "json"):
        """
        Save converted prompts to file in specified format.
        
        Args:
            results: Results dictionary from convert_dataset_prompts
            filename: Output filename (without extension)
            output_format: Output format - 'json' or 'csv'
        """
        if output_format.lower() == "csv":
            self._save_as_csv(results, filename)
        else:
            self._save_as_json(results, filename)
    
    def _save_as_json(self, results: Dict[str, Any], filename: str):
        """Save results as JSON file."""
        output_file = self.output_dir / f"{filename}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved converted prompts to JSON: {output_file}")
    
    def _save_as_csv(self, results: Dict[str, Any], filename: str):
        """Save results as CSV file."""
        output_file = self.output_dir / f"{filename}.csv"
        
        # Prepare data for CSV
        prompts_data = results.get("converted_prompts", [])
        
        if not prompts_data:
            logger.warning("No prompts to save")
            return
        
        # Increase CSV field size limit to handle large prompts
        csv.field_size_limit(1000000)  # Set to 1MB limit
        
        # Define CSV columns
        fieldnames = [
            "case_id", 
            "task", 
            "question", 
            "expected_answer", 
            "converted_prompt",
            "metadata_json"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for prompt_item in prompts_data:
                # Convert metadata to JSON string for CSV storage
                metadata_json = json.dumps(prompt_item.get("metadata", {}), ensure_ascii=False)
                
                row = {
                    "case_id": prompt_item.get("case_id", ""),
                    "task": prompt_item.get("task", ""),
                    "question": prompt_item.get("question", ""),
                    "expected_answer": prompt_item.get("expected_answer", ""),
                    "converted_prompt": prompt_item.get("converted_prompt", ""),
                    "metadata_json": metadata_json
                }
                writer.writerow(row)
        
        logger.info(f"Saved converted prompts to CSV: {output_file}")
        logger.info(f"CSV contains {len(prompts_data)} rows of prompt data")
    
    def convert_all_datasets(self, format: str = "json", max_cases: Optional[int] = None, output_format: str = "csv"):
        """
        Convert prompts for all available datasets.
        
        Args:
            format: Data format (json, xml, html, etc.)
            max_cases: Maximum cases per dataset/task
            output_format: Output format - 'json' or 'csv'
        """
        if not self.advanced_prompts_dir.exists():
            raise FileNotFoundError(f"Advanced prompts directory not found: {self.advanced_prompts_dir}")
        
        # Get all dataset directories
        datasets = [d.name for d in self.advanced_prompts_dir.iterdir() if d.is_dir()]
        
        for dataset in datasets:
            logger.info(f"Converting dataset: {dataset}")
            
            try:
                results = self.convert_dataset_prompts(dataset, format=format, max_cases=max_cases)
                filename = f"{dataset}_{format}_converted_prompts"
                self.save_converted_prompts(results, filename, output_format)
                
            except Exception as e:
                logger.error(f"Error converting dataset {dataset}: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert advanced prompt templates into actual LLM prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dataset", "-d",
        default="healthcare-dataset",
        help="Dataset to convert (default: healthcare-dataset)"
    )
    
    parser.add_argument(
        "--task", "-t",
        help="Specific task to convert (default: all tasks)"
    )
    
    parser.add_argument(
        "--format", "-f",
        default="json",
        choices=["json", "xml", "html", "md", "txt", "ttl"],
        help="Data format to use (default: json)"
    )
    
    parser.add_argument(
        "--max-cases", "-n",
        type=int,
        help="Maximum number of cases to convert"
    )
    
    parser.add_argument(
        "--all-datasets",
        action="store_true",
        help="Convert all available datasets"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default="converted_prompts",
        help="Output directory (default: converted_prompts)"
    )
    
    parser.add_argument(
        "--output-format", 
        default="csv",
        choices=["json", "csv"],
        help="Output file format (default: csv)"
    )
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = AdvancedPromptConverter(output_dir=args.output_dir)
    
    try:
        if args.all_datasets:
            logger.info("Converting all datasets...")
            converter.convert_all_datasets(format=args.format, max_cases=args.max_cases, output_format=args.output_format)
        else:
            logger.info(f"Converting dataset: {args.dataset}")
            results = converter.convert_dataset_prompts(
                dataset=args.dataset,
                task=args.task,
                format=args.format,
                max_cases=args.max_cases
            )
            
            # Generate filename (without extension, let save method add it)
            task_suffix = f"_{args.task}" if args.task else ""
            filename = f"{args.dataset}{task_suffix}_{args.format}_converted_prompts"
            
            converter.save_converted_prompts(results, filename, args.output_format)
        
        logger.info("Conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())