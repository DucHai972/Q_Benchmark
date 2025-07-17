"""
Benchmark Prompt Generator Module

This module creates benchmark prompts by combining prompt templates with data in different formats
to evaluate LLM performance across various data representations.
"""

import json
import os
import glob
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchmarkPromptGenerator:
    """
    Main class for generating benchmark prompts by combining templates with data.
    """
    
    def __init__(self, 
                 prompts_dir: str = "prompts",
                 benchmark_cache_dir: str = "benchmark_cache", 
                 preprocessed_data_dir: str = "preprocessed_data"):
        """
        Initialize the prompt generator.
        
        Args:
            prompts_dir: Directory containing prompt templates
            benchmark_cache_dir: Directory containing cached benchmark data
            preprocessed_data_dir: Directory containing full preprocessed datasets
        """
        self.prompts_dir = Path(prompts_dir)
        self.benchmark_cache_dir = Path(benchmark_cache_dir)
        self.preprocessed_data_dir = Path(preprocessed_data_dir)
        
        # Discovery
        self.datasets = self._discover_datasets()
        self.available_formats = ['json', 'xml', 'html', 'md', 'txt', 'ttl']
        
    def _discover_datasets(self) -> List[str]:
        """Discover available datasets from the prompts directory."""
        datasets = []
        if self.prompts_dir.exists():
            for item in self.prompts_dir.iterdir():
                if item.is_dir():
                    datasets.append(item.name)
        
        # Map prompt directory names to dataset names for consistency
        prompt_to_dataset_map = {
            'stack-overflow-2022': 'stack-overflow-2022-developer-survey',
            'self-reported-mental-health': 'self-reported-mental-health-college-students-2022'
        }
        
        # Convert prompt directory names to dataset names
        mapped_datasets = []
        for dataset in datasets:
            if dataset in prompt_to_dataset_map:
                mapped_datasets.append(prompt_to_dataset_map[dataset])
            else:
                mapped_datasets.append(dataset)
        
        return mapped_datasets
    
    def _get_available_tasks(self, dataset: str) -> List[str]:
        """Get available task types for a given dataset."""
        tasks = set()
        
        # Map dataset names back to prompt directory names
        dataset_to_prompt_map = {
            'stack-overflow-2022-developer-survey': 'stack-overflow-2022',
            'self-reported-mental-health-college-students-2022': 'self-reported-mental-health'
        }
        
        prompt_dir = dataset_to_prompt_map.get(dataset, dataset)
        prompt_files = list(self.prompts_dir.glob(f"{prompt_dir}/*.json"))
        
        for file_path in prompt_files:
            # Extract task from filename like "dataset_task_qa_pairs.json"
            filename = file_path.stem
            if "_qa_pairs" in filename:
                task = filename.replace(f"{prompt_dir}_", "").replace("_qa_pairs", "")
                tasks.add(task)
        return sorted(list(tasks))
    
    def load_prompt_templates(self, dataset: str, task: str) -> List[Dict[str, Any]]:
        """
        Load prompt templates for a specific dataset and task.
        
        Args:
            dataset: Dataset name (e.g., 'healthcare-dataset')
            task: Task type (e.g., 'answer_lookup')
            
        Returns:
            List of prompt template dictionaries
        """
        # Map dataset names back to prompt directory names
        dataset_to_prompt_map = {
            'stack-overflow-2022-developer-survey': 'stack-overflow-2022',
            'self-reported-mental-health-college-students-2022': 'self-reported-mental-health'
        }
        
        prompt_dir = dataset_to_prompt_map.get(dataset, dataset)
        json_file = self.prompts_dir / prompt_dir / f"{prompt_dir}_{task}_qa_pairs.json"
        
        if not json_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {json_file}")
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            logger.info(f"Loaded {len(templates)} prompt templates for {dataset}/{task}")
            return templates
        except Exception as e:
            logger.error(f"Error loading prompt templates: {e}")
            raise
    
    def load_case_data(self, dataset: str, task: str, case_id: str, data_format: str) -> str:
        """
        Load specific case data in the requested format.
        
        Args:
            dataset: Dataset name
            task: Task type
            case_id: Case identifier (e.g., 'case_1')
            data_format: Data format ('json', 'xml', 'html', 'md', 'txt', 'ttl')
            
        Returns:
            Data content as string
        """
        data_file = (self.benchmark_cache_dir / dataset / task / 
                    data_format / f"{case_id}.{data_format}")
        
        if not data_file.exists():
            raise FileNotFoundError(f"Case data not found: {data_file}")
            
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded case data: {data_file}")
            return content
        except Exception as e:
            logger.error(f"Error loading case data: {e}")
            raise
    
    def load_full_dataset(self, dataset: str, data_format: str) -> str:
        """
        Load the full dataset in the requested format.
        
        Args:
            dataset: Dataset name
            data_format: Data format
            
        Returns:
            Full dataset content as string
        """
        # Map dataset names to their file patterns
        dataset_file_map = {
            'healthcare-dataset': 'healthcare_questionnaire',
            'isbar': 'isbar_questionnaire', 
            'self-reported-mental-health-college-students-2022': 'mental_health_questionnaire',
            'stack-overflow-2022-developer-survey': 'survey_results_sample',
            'sus-uta7': 'sus_uta7_questionnaire'
        }
        
        if dataset not in dataset_file_map:
            raise ValueError(f"Unknown dataset: {dataset}")
            
        filename = f"{dataset_file_map[dataset]}.{data_format}"
        data_file = self.preprocessed_data_dir / dataset / filename
        
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {data_file}")
            
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded full dataset: {data_file}")
            return content
        except Exception as e:
            logger.error(f"Error loading full dataset: {e}")
            raise
    
    def generate_prompt(self, 
                       dataset: str, 
                       task: str, 
                       case_id: str, 
                       data_format: str,
                       use_full_dataset: bool = False) -> Dict[str, Any]:
        """
        Generate a complete prompt by combining template with data.
        
        Args:
            dataset: Dataset name
            task: Task type
            case_id: Case identifier
            data_format: Data format for the data block
            use_full_dataset: If True, use full dataset instead of case-specific data
            
        Returns:
            Dictionary containing the complete prompt and metadata
        """
        # Load the prompt template
        templates = self.load_prompt_templates(dataset, task)
        template = None
        for t in templates:
            if t['case_id'] == case_id:
                template = t
                break
                
        if not template:
            raise ValueError(f"Template not found for case {case_id}")
        
        # Load the appropriate data
        if use_full_dataset:
            data_content = self.load_full_dataset(dataset, data_format)
        else:
            data_content = self.load_case_data(dataset, task, case_id, data_format)
        
        # Generate the complete prompt
        complete_prompt = template['prompt'].replace(
            '[Insert the full data block here]', 
            data_content
        )
        
        return {
            'case_id': case_id,
            'dataset': dataset,
            'task': task,
            'data_format': data_format,
            'prompt': complete_prompt,
            'expected_answer': template.get('expected_answer'),
            'metadata': template.get('metadata', {}),
            'use_full_dataset': use_full_dataset
        }
    
    def generate_format_comparison_prompts(self, 
                                         dataset: str, 
                                         task: str, 
                                         case_id: str,
                                         formats: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate prompts for the same case across multiple data formats.
        
        Args:
            dataset: Dataset name
            task: Task type
            case_id: Case identifier
            formats: List of formats to generate (defaults to all available)
            
        Returns:
            List of prompt dictionaries, one for each format
        """
        if formats is None:
            formats = self.available_formats
            
        prompts = []
        for fmt in formats:
            try:
                prompt = self.generate_prompt(dataset, task, case_id, fmt)
                prompts.append(prompt)
            except FileNotFoundError as e:
                logger.warning(f"Skipping format {fmt} for {case_id}: {e}")
                continue
                
        return prompts
    
    def generate_benchmark_suite(self, 
                               dataset: Optional[str] = None,
                               task: Optional[str] = None, 
                               max_cases: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate a comprehensive benchmark suite.
        
        Args:
            dataset: Specific dataset (None for all)
            task: Specific task (None for all)
            max_cases: Maximum number of cases per task/dataset combination
            
        Returns:
            List of all generated prompts
        """
        all_prompts = []
        
        datasets_to_process = [dataset] if dataset else self.datasets
        
        for ds in datasets_to_process:
            available_tasks = self._get_available_tasks(ds)
            tasks_to_process = [task] if task else available_tasks
            
            for t in tasks_to_process:
                try:
                    # Load templates to get case IDs
                    templates = self.load_prompt_templates(ds, t)
                    cases_to_process = templates[:max_cases] if max_cases else templates
                    
                    for template in cases_to_process:
                        case_id = template['case_id']
                        # Generate prompts for all available formats
                        format_prompts = self.generate_format_comparison_prompts(ds, t, case_id)
                        all_prompts.extend(format_prompts)
                        
                except Exception as e:
                    logger.error(f"Error processing {ds}/{t}: {e}")
                    continue
                    
        logger.info(f"Generated {len(all_prompts)} benchmark prompts")
        return all_prompts
    
    def save_benchmark_prompts(self, 
                             prompts: List[Dict[str, Any]], 
                             output_file: str = "benchmark_prompts.json"):
        """
        Save generated prompts to a file.
        
        Args:
            prompts: List of prompt dictionaries
            output_file: Output filename
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(prompts)} prompts to {output_file}")
        except Exception as e:
            logger.error(f"Error saving prompts: {e}")
            raise
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets."""
        return self.datasets
    
    def get_available_tasks(self, dataset: str) -> List[str]:
        """Get available tasks for a dataset."""
        return self._get_available_tasks(dataset)
    
    def get_metadata(self, dataset: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata about datasets and their capabilities.
        
        Args:
            dataset: Specific dataset (None for all)
            
        Returns:
            Metadata dictionary
        """
        if dataset:
            metadata_file = self.benchmark_cache_dir / dataset / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "dataset": dataset,
                    "tasks": self._get_available_tasks(dataset),
                    "formats": self.available_formats
                }
        else:
            metadata = {}
            for ds in self.datasets:
                metadata[ds] = self.get_metadata(ds)
            return metadata


def main():
    """Example usage and testing."""
    generator = BenchmarkPromptGenerator()
    
    # Print available datasets and tasks
    print("Available datasets:")
    for dataset in generator.get_available_datasets():
        print(f"  {dataset}")
        tasks = generator.get_available_tasks(dataset)
        print(f"    Tasks: {', '.join(tasks)}")
    
    # Generate a single prompt example
    if generator.datasets:
        dataset = generator.datasets[0]  # Use first available dataset
        tasks = generator.get_available_tasks(dataset)
        if tasks:
            task = tasks[0]  # Use first available task
            try:
                # Generate prompts for different formats
                prompts = generator.generate_format_comparison_prompts(
                    dataset, task, "case_1", formats=['json', 'xml', 'md']
                )
                
                print(f"\nGenerated {len(prompts)} prompts for {dataset}/{task}/case_1")
                
                # Show first prompt as example
                if prompts:
                    first_prompt = prompts[0]
                    print(f"\nExample prompt (format: {first_prompt['data_format']}):")
                    print("=" * 80)
                    print(first_prompt['prompt'][:500] + "..." if len(first_prompt['prompt']) > 500 else first_prompt['prompt'])
                    print("=" * 80)
                    
            except Exception as e:
                print(f"Error generating example: {e}")


if __name__ == "__main__":
    main() 