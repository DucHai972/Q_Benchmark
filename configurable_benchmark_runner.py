"""
Configurable Benchmark Runner

This script runs benchmarks using different prompt configurations with Gemini 1.5 Flash,
testing 10 cases per task across all formats and saving both results and prompts.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from dotenv import load_dotenv
from dataclasses import dataclass

from llm_clients import GoogleClient
from evaluator import BenchmarkEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """Configuration for prompt generation."""
    include_one_shot: bool = True      # Include one-shot example
    include_partition: bool = True     # Include partition marks like <example>, <task>
    include_role: bool = True          # Include role prompting
    include_format: bool = True        # Include format explanation
    data_at_end: bool = False         # Put questionnaire data at the end instead of middle


class ConfigurableAdvancedPromptGenerator:
    """
    Generator for configurable advanced template-based prompts.
    """
    
    def __init__(self, 
                 advanced_prompts_dir: str = "advanced_prompts",
                 benchmark_cache_dir: str = "benchmark_cache", 
                 preprocessed_data_dir: str = "preprocessed_data"):
        """
        Initialize the configurable advanced prompt generator.
        """
        self.advanced_prompts_dir = Path(advanced_prompts_dir)
        self.benchmark_cache_dir = Path(benchmark_cache_dir)
        self.preprocessed_data_dir = Path(preprocessed_data_dir)
        
        # Discovery
        self.datasets = self._discover_datasets()
        self.available_formats = ['json', 'xml', 'html', 'md', 'txt', 'ttl']
        
    def _discover_datasets(self) -> List[str]:
        """Discover available datasets from the advanced_prompts directory."""
        datasets = []
        if self.advanced_prompts_dir.exists():
            for item in self.advanced_prompts_dir.iterdir():
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
        prompt_files = list(self.advanced_prompts_dir.glob(f"{prompt_dir}/*.json"))
        
        for file_path in prompt_files:
            # Extract task from filename like "dataset_task_qa_pairs.json"
            filename = file_path.stem
            if "_qa_pairs" in filename:
                task = filename.replace(f"{prompt_dir}_", "").replace("_qa_pairs", "")
                tasks.add(task)
        return sorted(list(tasks))
    
    def load_advanced_prompt_templates(self, dataset: str, task: str) -> List[Dict[str, Any]]:
        """Load advanced prompt templates for a specific dataset and task."""
        # Map dataset names back to prompt directory names
        dataset_to_prompt_map = {
            'stack-overflow-2022-developer-survey': 'stack-overflow-2022',
            'self-reported-mental-health-college-students-2022': 'self-reported-mental-health'
        }
        
        prompt_dir = dataset_to_prompt_map.get(dataset, dataset)
        json_file = self.advanced_prompts_dir / prompt_dir / f"{prompt_dir}_{task}_qa_pairs.json"
        
        if not json_file.exists():
            raise FileNotFoundError(f"Advanced prompt file not found: {json_file}")
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            logger.debug(f"Loaded {len(templates)} advanced prompt templates for {dataset}/{task}")
            return templates
        except Exception as e:
            logger.error(f"Error loading advanced prompt templates: {e}")
            raise
    
    def load_case_data(self, dataset: str, task: str, case_id: str, data_format: str) -> str:
        """Load specific case data in the requested format."""
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
    
    def create_case1_example_with_data(self, dataset: str, task: str, data_format: str, 
                                     templates: List[Dict[str, Any]], config: PromptConfig) -> str:
        """Create the CASE_1 example with actual case_1 data inserted."""
        if not config.include_one_shot:
            return ""
        
        # Find case_1 template
        case_1_template = None
        for template in templates:
            if template['case_id'] == 'case_1':
                case_1_template = template
                break
        
        if not case_1_template:
            raise ValueError("case_1 template not found")
        
        # Load case_1 data
        try:
            case_1_data = self.load_case_data(dataset, task, 'case_1', data_format)
        except FileNotFoundError:
            logger.warning(f"case_1 data not found for {dataset}/{task}/{data_format}, using original template")
            return case_1_template.get('CASE_1', '')
        
        # Get the question from case_1
        case_1_question = case_1_template.get('question', '')
        case_1_answer = case_1_template.get('expected_answer', '')
        
        # Create the complete CASE_1 example with real data
        if config.include_partition:
            case_1_with_data = f"<example>\n{case_1_question}\n\nDATA:\n\n{case_1_data}\n\nAnswer: {case_1_answer}\n</example>"
        else:
            case_1_with_data = f"{case_1_question}\n\nDATA:\n\n{case_1_data}\n\nAnswer: {case_1_answer}"
        
        return case_1_with_data
    
    def assemble_configurable_prompt(self, template: Dict[str, Any], data_content: str, 
                                   case_1_with_data: str, config: PromptConfig) -> str:
        """Assemble the configurable prompt by replacing template placeholders with actual content."""
        components = []
        
        # Add components based on configuration
        if config.include_one_shot and case_1_with_data:
            components.append(case_1_with_data)
        
        if not config.data_at_end:
            # Add questionnaire data in normal position
            if config.include_partition:
                components.append(f"<questionnaire>\n{data_content}\n</questionnaire>")
            else:
                components.append(f"DATA:\n\n{data_content}")
        
        if config.include_role:
            components.append(template.get('ROLE_PROMPTING', ''))
        
        if config.include_format:
            components.append(template.get('FORMAT_EXPLANATION', ''))
        
        # Add output instructions (always include these)
        components.append(template.get('OUTPUT_INSTRUCTIONS', ''))
        
        # Add the task question
        question = template.get('question', '')
        if config.include_partition:
            components.append(f"<task>\n{question}\n</task>")
        else:
            components.append(f"QUESTION:\n{question}")
        
        if config.data_at_end:
            # Add questionnaire data at the end
            if config.include_partition:
                components.append(f"<questionnaire>\n{data_content}\n</questionnaire>")
            else:
                components.append(f"DATA:\n\n{data_content}")
        
        # Join all components with double newlines
        assembled_prompt = "\n\n".join(filter(None, components))
        
        return assembled_prompt
    
    def generate_configurable_prompt(self, 
                                   dataset: str, 
                                   task: str, 
                                   case_id: str, 
                                   data_format: str,
                                   config: PromptConfig) -> Dict[str, Any]:
        """Generate a complete configurable prompt by combining template with data."""
        # Load all templates for this dataset/task
        templates = self.load_advanced_prompt_templates(dataset, task)
        
        # Find the specific template for this case
        template = None
        for t in templates:
            if t['case_id'] == case_id:
                template = t
                break
                
        if not template:
            raise ValueError(f"Advanced template not found for case {case_id}")
        
        # Create the CASE_1 example with real data
        case_1_with_data = self.create_case1_example_with_data(dataset, task, data_format, templates, config)
        
        # Load the appropriate data for the current case
        data_content = self.load_case_data(dataset, task, case_id, data_format)
        
        # Assemble the complete configurable prompt
        complete_prompt = self.assemble_configurable_prompt(template, data_content, case_1_with_data, config)
        
        return {
            'case_id': case_id,
            'dataset': dataset,
            'task': task,
            'data_format': data_format,
            'prompt': complete_prompt,
            'expected_answer': template.get('expected_answer'),
            'metadata': template.get('metadata', {}),
            'config': {
                'include_one_shot': config.include_one_shot,
                'include_partition': config.include_partition,
                'include_role': config.include_role,
                'include_format': config.include_format,
                'data_at_end': config.data_at_end
            }
        }


class ConfigurableBenchmarkRunner:
    """
    Runs benchmarks using configurable prompts with Gemini 1.5 Flash.
    """
    
    def __init__(self, config: PromptConfig, config_name: str, 
                 output_dir: str = "benchmark_results/benchmark_google"):
        """
        Initialize the configurable benchmark runner.
        
        Args:
            config: Prompt configuration to use
            config_name: Name for this configuration
            output_dir: Base directory to save benchmark results
        """
        load_dotenv()
        
        self.config = config
        self.config_name = config_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.prompt_generator = ConfigurableAdvancedPromptGenerator()
        self.evaluator = BenchmarkEvaluator()
        
        # Initialize Google client
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it in your .env file.")
        
        self.llm_client = GoogleClient(api_key, model_name="gemini-1.5-flash")
        
        # Available formats
        self.formats = ['html', 'json', 'md', 'ttl', 'txt', 'xml']
        
        logger.info(f"Initialized Configurable Benchmark Runner: {config_name}")
    
    def save_prompt_to_file(self, prompt_data: Dict[str, Any], run_dir: Path) -> str:
        """Save the actual prompt sent to LLM for analysis."""
        
        # Create prompts directory
        prompts_dir = run_dir / "prompts" / prompt_data['dataset'] / prompt_data['task'] / prompt_data['data_format']
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create prompt filename
        prompt_file = prompts_dir / f"{prompt_data['case_id']}.txt"
        
        # Format prompt content
        content = []
        content.append("=" * 80)
        content.append(f"PROMPT SENT TO LLM - {self.config_name.upper()}")
        content.append("=" * 80)
        content.append(f"Dataset: {prompt_data['dataset']}")
        content.append(f"Task: {prompt_data['task']}")
        content.append(f"Case: {prompt_data['case_id']}")
        content.append(f"Format: {prompt_data['data_format']}")
        content.append(f"Expected Answer: {prompt_data['expected_answer']}")
        content.append("")
        content.append("Configuration:")
        config = prompt_data['config']
        content.append(f"• One-shot example: {config['include_one_shot']}")
        content.append(f"• Partition marks: {config['include_partition']}")
        content.append(f"• Role prompting: {config['include_role']}")
        content.append(f"• Format explanation: {config['include_format']}")
        content.append(f"• Data at end: {config['data_at_end']}")
        content.append("")
        content.append("=" * 80)
        content.append("ACTUAL PROMPT")
        content.append("=" * 80)
        content.append("")
        content.append(prompt_data['prompt'])
        
        # Write to file
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        
        return str(prompt_file)
    
    def run_single_case(self, dataset: str, task: str, case_id: str, data_format: str, run_dir: Path) -> Dict[str, Any]:
        """Run benchmark for a single case."""
        try:
            # Generate the configurable prompt
            prompt_data = self.prompt_generator.generate_configurable_prompt(
                dataset, task, case_id, data_format, self.config
            )
            
            # Save the prompt to file
            prompt_file = self.save_prompt_to_file(prompt_data, run_dir)
            
            # Send prompt to LLM
            llm_result = self.llm_client.generate(prompt_data['prompt'], max_tokens=1000)
            
            # Evaluate the result
            evaluation = self.evaluator.evaluate_response(
                llm_result['response'], 
                prompt_data['expected_answer'],
                task_type=task
            )
            
            # Combine all results
            result = {
                'case_id': case_id,
                'dataset': dataset,
                'task': task,
                'data_format': data_format,
                'config_name': self.config_name,
                'question': prompt_data['metadata'].get('lookup_question', prompt_data.get('question', '')),
                'expected_answer': prompt_data['expected_answer'],
                'llm_response': llm_result['response'],
                'llm_success': llm_result['success'],
                'llm_error': llm_result['error'],
                'response_time': llm_result['response_time'],
                'model': llm_result['model'],
                'provider': llm_result['provider'],
                'evaluation_correct': evaluation.get('exact_match', False),
                'evaluation_score': evaluation.get('score', 0.0),
                'evaluation_exact_match': evaluation.get('exact_match', False),
                'evaluation_normalized_match': evaluation.get('normalized_match', False),
                'evaluation_partial_match': evaluation.get('partial_match', False),
                'evaluation_details': evaluation,
                'prompt_file': prompt_file,
                'config': prompt_data['config'],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f"Completed {dataset}/{task}/{case_id}/{data_format}: {'✓' if evaluation.get('exact_match', False) else '✗'}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {dataset}/{task}/{case_id}/{data_format}: {e}")
            return {
                'case_id': case_id,
                'dataset': dataset,
                'task': task,
                'data_format': data_format,
                'config_name': self.config_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_dataset_task(self, dataset: str, task: str, run_dir: Path, max_cases: int = 10) -> List[Dict[str, Any]]:
        """Run benchmark for all cases and formats in a dataset/task."""
        results = []
        
        try:
            # Load templates to get case IDs
            templates = self.prompt_generator.load_advanced_prompt_templates(dataset, task)
            cases_to_process = templates[:max_cases] if max_cases else templates
            
            # Run benchmark for each case and format
            total_operations = len(cases_to_process) * len(self.formats)
            with tqdm(total=total_operations, desc=f"Running {dataset}/{task} ({self.config_name})") as pbar:
                for template in cases_to_process:
                    case_id = template['case_id']
                    
                    for data_format in self.formats:
                        try:
                            result = self.run_single_case(dataset, task, case_id, data_format, run_dir)
                            results.append(result)
                        except Exception as e:
                            logger.warning(f"Skipping {case_id}/{data_format}: {e}")
                        
                        pbar.update(1)
            
            logger.info(f"Completed {dataset}/{task}: {len(results)} results")
            
        except Exception as e:
            logger.error(f"Error processing dataset/task {dataset}/{task}: {e}")
        
        return results
    
    def run_all_datasets(self, max_cases_per_task: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Run benchmark for all datasets and tasks."""
        
        # Create run directory
        run_id = f"config_{self.config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir = self.output_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        all_results = {}
        
        for dataset in self.prompt_generator.datasets:
            logger.info(f"Processing dataset: {dataset}")
            
            try:
                available_tasks = self.prompt_generator._get_available_tasks(dataset)
                
                for task in available_tasks:
                    key = f"{dataset}/{task}"
                    results = self.run_dataset_task(dataset, task, run_dir, max_cases_per_task)
                    all_results[key] = results
                    
            except Exception as e:
                logger.error(f"Error processing dataset {dataset}: {e}")
                continue
        
        # Save results
        self.save_results(all_results, run_dir)
        
        return all_results
    
    def save_results(self, results: Dict[str, List[Dict[str, Any]]], run_dir: Path) -> str:
        """Save benchmark results to files."""
        
        # Flatten all results for summary
        all_results = []
        for dataset_task, task_results in results.items():
            all_results.extend(task_results)
        
        # Save detailed JSON results
        json_file = run_dir / "detailed_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save summary Excel files
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Overall summary
            excel_file = run_dir / "benchmark_summary.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Results', index=False)
                
                # Summary by format
                if 'data_format' in df.columns and 'evaluation_correct' in df.columns:
                    format_summary = df.groupby('data_format')['evaluation_correct'].agg(['count', 'sum', 'mean']).reset_index()
                    format_summary.columns = ['Data Format', 'Total Cases', 'Correct', 'Accuracy']
                    format_summary.to_excel(writer, sheet_name='Format Summary', index=False)
                
                # Summary by task
                if 'task' in df.columns and 'evaluation_correct' in df.columns:
                    task_summary = df.groupby('task')['evaluation_correct'].agg(['count', 'sum', 'mean']).reset_index()
                    task_summary.columns = ['Task', 'Total Cases', 'Correct', 'Accuracy']
                    task_summary.to_excel(writer, sheet_name='Task Summary', index=False)
        
        # Save metadata
        metadata = {
            'run_id': run_dir.name,
            'config_name': self.config_name,
            'config': {
                'include_one_shot': self.config.include_one_shot,
                'include_partition': self.config.include_partition,
                'include_role': self.config.include_role,
                'include_format': self.config.include_format,
                'data_at_end': self.config.data_at_end
            },
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-1.5-flash',
            'provider': 'google',
            'total_results': len(all_results),
            'datasets': list(set(r.get('dataset', '') for r in all_results)),
            'tasks': list(set(r.get('task', '') for r in all_results)),
            'formats': self.formats,
            'cases_per_task': 10
        }
        
        metadata_file = run_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved results to: {run_dir}")
        return str(run_dir)
    
    def run_benchmark(self) -> str:
        """Run the complete benchmark and save results."""
        logger.info(f"🚀 Starting Configurable Benchmark: {self.config_name}")
        logger.info(f"📊 Testing {len(self.formats)} formats: {', '.join(self.formats)}")
        logger.info(f"📋 Using 10 cases per task")
        
        # Run all benchmarks
        results = self.run_all_datasets(max_cases_per_task=10)
        
        # Print summary
        total_results = sum(len(task_results) for task_results in results.values())
        successful_results = sum(1 for task_results in results.values() 
                               for result in task_results 
                               if result.get('evaluation_correct', False))
        
        logger.info(f"✅ Benchmark Complete: {self.config_name}")
        logger.info(f"🎯 Total cases: {total_results}")
        logger.info(f"✅ Successful: {successful_results}")
        logger.info(f"📊 Accuracy: {successful_results/total_results*100:.1f}%" if total_results > 0 else "No results")
        
        return f"Completed {self.config_name}"


def get_all_configurations() -> Dict[str, PromptConfig]:
    """Get all available prompt configurations."""
    
    return {
        "default": PromptConfig(),
        "no_one_shot": PromptConfig(include_one_shot=False),
        "no_partition": PromptConfig(include_partition=False),
        "no_role": PromptConfig(include_role=False),
        "no_format": PromptConfig(include_format=False),
        "data_at_end": PromptConfig(data_at_end=True)
    }


def main():
    """Main function to run all configuration benchmarks."""
    
    print("⚙️ Configurable Benchmark Runner")
    print("=" * 60)
    
    configurations = get_all_configurations()
    
    print(f"🔧 Will run {len(configurations)} configurations:")
    for config_name, config in configurations.items():
        print(f"  • {config_name}")
    
    print(f"\n📊 Each configuration will test:")
    print(f"  • 10 cases per task")
    print(f"  • 6 data formats (html, json, md, ttl, txt, xml)")
    print(f"  • 5 datasets")
    print(f"  • 6 tasks per dataset")
    print(f"  • Total: ~1,800 cases per configuration")
    
    # Run benchmarks for each configuration
    results = []
    for config_name, config in configurations.items():
        print(f"\n🚀 Running benchmark for: {config_name}")
        print("-" * 40)
        
        try:
            runner = ConfigurableBenchmarkRunner(config, config_name)
            result = runner.run_benchmark()
            results.append(result)
        except Exception as e:
            print(f"❌ Error running {config_name}: {e}")
            logger.error(f"Error running {config_name}: {e}")
            continue
    
    print(f"\n🎉 All Benchmarks Complete!")
    print(f"✅ Successfully completed: {len(results)} configurations")
    print(f"📁 Results saved in: benchmark_results/benchmark_google/")
    print(f"📋 Each run includes:")
    print(f"  • detailed_results.json - Full benchmark data")
    print(f"  • benchmark_summary.xlsx - Excel summaries")
    print(f"  • metadata.json - Configuration and run details") 
    print(f"  • prompts/ - Actual prompts sent to LLM")


if __name__ == "__main__":
    main() 