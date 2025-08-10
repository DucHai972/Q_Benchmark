#!/usr/bin/env python3
"""
Fill Blank Responses Script

This script identifies blank responses in gpt-4.1-mini CSV files and fills them
by re-running the prompts through the appropriate LLM models.
"""

import os
import csv
import time
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import glob
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import LLM clients from benchmark_pipeline
try:
    from benchmark_pipeline import SimpleOpenAIClient, SimpleGoogleClient, SimpleEvaluator
except ImportError:
    logger.error("Could not import LLM clients from benchmark_pipeline.py")
    raise


class BlankResponseFiller:
    """Fill blank responses in benchmark CSV files"""
    
    def __init__(self, benchmark_results_dir: str = "benchmark_results", dry_run: bool = False):
        load_dotenv()
        
        self.benchmark_results_dir = Path(benchmark_results_dir)
        self.dry_run = dry_run
        self.evaluator = SimpleEvaluator()
        
        # Initialize LLM clients
        self.clients = self._initialize_clients()
        
        # Statistics
        self.stats = {
            'total_blank_found': 0,
            'total_filled': 0,
            'total_errors': 0,
            'files_processed': 0
        }
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize LLM clients based on available API keys"""
        clients = {}
        
        # OpenAI clients
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                clients['gpt-4.1-mini'] = SimpleOpenAIClient(openai_key, "gpt-4o-mini")
                clients['gpt-3.5-turbo'] = SimpleOpenAIClient(openai_key, "gpt-3.5-turbo")
                clients['gpt-4o-mini'] = SimpleOpenAIClient(openai_key, "gpt-4o-mini")
                clients['gpt-5-mini'] = SimpleOpenAIClient(openai_key, "gpt-4o-mini")  # Fallback
                clients['gpt-5'] = SimpleOpenAIClient(openai_key, "gpt-4o")  # Fallback
                logger.info("OpenAI clients initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI clients: {e}")
        else:
            logger.warning("OPENAI_API_KEY not found")
        
        # Google clients  
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            try:
                clients['gemini-1.5-flash'] = SimpleGoogleClient(google_key, "gemini-1.5-flash")
                clients['gemini-1.5-pro'] = SimpleGoogleClient(google_key, "gemini-1.5-pro")
                clients['gemini-2.5-flash'] = SimpleGoogleClient(google_key, "gemini-1.5-flash")  # Fallback
                logger.info("Google clients initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google clients: {e}")
        else:
            logger.warning("GOOGLE_API_KEY not found")
        
        return clients
    
    def _get_model_client(self, model_dir_name: str) -> Optional[Any]:
        """Get appropriate client for model directory"""
        # Extract base model name from directory (remove variant suffixes)
        if model_dir_name.startswith('gpt-4.1-mini'):
            return self.clients.get('gpt-4.1-mini')
        elif model_dir_name.startswith('gpt-3.5-turbo'):
            return self.clients.get('gpt-3.5-turbo')
        elif model_dir_name.startswith('gpt-4o-mini'):
            return self.clients.get('gpt-4o-mini')
        elif model_dir_name.startswith('gpt-5-mini'):
            return self.clients.get('gpt-5-mini')
        elif model_dir_name.startswith('gpt-5'):
            return self.clients.get('gpt-5')
        elif model_dir_name.startswith('gemini-1.5-flash'):
            return self.clients.get('gemini-1.5-flash')
        elif model_dir_name.startswith('gemini-1.5-pro'):
            return self.clients.get('gemini-1.5-pro')
        elif model_dir_name.startswith('gemini-2.5-flash'):
            return self.clients.get('gemini-2.5-flash')
        else:
            logger.warning(f"No client mapping found for model directory: {model_dir_name}")
            return None
    
    def _backup_file(self, file_path: Path) -> Path:
        """Create backup of original file"""
        backup_path = file_path.with_suffix('.csv.backup')
        if not backup_path.exists():
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        return backup_path
    
    def _is_response_blank(self, response: Any) -> bool:
        """Check if response is blank/empty"""
        if pd.isna(response):
            return True
        if isinstance(response, str) and response.strip() == '':
            return True
        return False
    
    def fill_csv_file(self, csv_file_path: Path, model_dir_name: str) -> bool:
        """Fill blank responses in a single CSV file"""
        logger.info(f"Processing {csv_file_path}")
        
        # Get appropriate client
        client = self._get_model_client(model_dir_name)
        if not client:
            logger.error(f"No client available for model: {model_dir_name}")
            return False
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Check if required columns exist
            required_cols = ['prompt', 'Response', 'expected_answer']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"Missing required columns in {csv_file_path}. Required: {required_cols}")
                return False
            
            # Find blank responses
            blank_mask = df['Response'].apply(self._is_response_blank)
            blank_indices = df[blank_mask].index.tolist()
            
            if not blank_indices:
                logger.info(f"No blank responses found in {csv_file_path}")
                return True
            
            logger.info(f"Found {len(blank_indices)} blank responses in {csv_file_path}")
            self.stats['total_blank_found'] += len(blank_indices)
            
            if not self.dry_run:
                # Create backup before modifying
                self._backup_file(csv_file_path)
            
            filled_count = 0
            for idx in blank_indices:
                prompt = df.loc[idx, 'prompt']
                expected_answer = df.loc[idx, 'expected_answer']
                
                if pd.isna(prompt) or prompt.strip() == '':
                    logger.warning(f"Empty prompt at index {idx}, skipping")
                    continue
                
                logger.info(f"Filling response for index {idx}")
                
                if self.dry_run:
                    logger.info(f"DRY RUN: Would fill response at index {idx}")
                    filled_count += 1
                    continue
                
                # Generate response using LLM
                try:
                    result = client.generate(prompt, max_tokens=1000)
                    
                    if result['success']:
                        response = result['response']
                        df.loc[idx, 'Response'] = response
                        
                        # Evaluate the response
                        evaluation = self.evaluator.evaluate_response(response, expected_answer)
                        df.loc[idx, 'Correct'] = evaluation['correct']
                        
                        filled_count += 1
                        logger.info(f"Successfully filled response at index {idx}")
                        
                        # Add delay to respect rate limits
                        time.sleep(0.5)
                        
                    else:
                        logger.error(f"Failed to generate response at index {idx}: {result['error']}")
                        self.stats['total_errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing index {idx}: {e}")
                    self.stats['total_errors'] += 1
                    continue
            
            # Save updated CSV
            if not self.dry_run and filled_count > 0:
                df.to_csv(csv_file_path, index=False)
                logger.info(f"Updated {csv_file_path} with {filled_count} new responses")
            
            self.stats['total_filled'] += filled_count
            return True
            
        except Exception as e:
            logger.error(f"Error processing {csv_file_path}: {e}")
            return False
    
    def process_model_directory(self, model_dir: Path) -> None:
        """Process all CSV files in a model directory"""
        model_dir_name = model_dir.name
        logger.info(f"Processing model directory: {model_dir_name}")
        
        # Find all CSV files
        csv_files = list(model_dir.rglob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No CSV files found in {model_dir}")
            return
        
        logger.info(f"Found {len(csv_files)} CSV files in {model_dir_name}")
        
        for csv_file in csv_files:
            try:
                success = self.fill_csv_file(csv_file, model_dir_name)
                if success:
                    self.stats['files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
                continue
    
    def process_all_gpt_directories(self) -> None:
        """Process all gpt-4.1-mini directories and variants"""
        if not self.benchmark_results_dir.exists():
            logger.error(f"Benchmark results directory not found: {self.benchmark_results_dir}")
            return
        
        # Find all gpt-4.1-mini directories
        gpt_dirs = [d for d in self.benchmark_results_dir.iterdir() 
                   if d.is_dir() and d.name.startswith('gpt-4.1-mini')]
        
        if not gpt_dirs:
            logger.warning("No gpt-4.1-mini directories found")
            return
        
        logger.info(f"Found {len(gpt_dirs)} gpt-4.1-mini directories")
        
        for model_dir in sorted(gpt_dirs):
            self.process_model_directory(model_dir)
    
    def print_stats(self) -> None:
        """Print processing statistics"""
        print("\n" + "="*50)
        print("BLANK RESPONSE FILLING STATISTICS")
        print("="*50)
        print(f"Total blank responses found: {self.stats['total_blank_found']}")
        print(f"Total responses filled: {self.stats['total_filled']}")
        print(f"Total errors: {self.stats['total_errors']}")
        print(f"Files processed: {self.stats['files_processed']}")
        
        if self.dry_run:
            print("\nThis was a DRY RUN - no files were modified")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fill blank responses in gpt-4.1-mini benchmark results")
    parser.add_argument('--benchmark-dir', default='benchmark_results', 
                       help='Path to benchmark results directory')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--model-dir', type=str, 
                       help='Process only specific model directory (e.g., gpt-4.1-mini_wo_oneshot)')
    
    args = parser.parse_args()
    
    # Initialize filler
    filler = BlankResponseFiller(args.benchmark_dir, dry_run=args.dry_run)
    
    if not filler.clients:
        logger.error("No LLM clients available. Please check your API keys in .env file")
        return
    
    logger.info(f"Available clients: {list(filler.clients.keys())}")
    
    if args.model_dir:
        # Process specific model directory
        model_dir = Path(args.benchmark_dir) / args.model_dir
        if model_dir.exists():
            filler.process_model_directory(model_dir)
        else:
            logger.error(f"Model directory not found: {model_dir}")
    else:
        # Process all gpt-4.1-mini directories
        filler.process_all_gpt_directories()
    
    filler.print_stats()


if __name__ == "__main__":
    main()