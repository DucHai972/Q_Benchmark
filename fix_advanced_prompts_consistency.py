#!/usr/bin/env python3
"""
Fix advanced_prompts consistency by adding missing XML tags

This script fixes the prompt templates in sus-uta7, stack-overflow-2022, 
and self-reported-mental-health datasets to match the consistent format 
used by healthcare-dataset and isbar.
"""

import json
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedPromptsConsistencyFixer:
    def __init__(self, advanced_prompts_dir: str = "advanced_prompts"):
        self.advanced_prompts_dir = Path(advanced_prompts_dir)
        
        # Datasets that need fixing
        self.datasets_to_fix = [
            'sus-uta7',
            'stack-overflow-2022', 
            'self-reported-mental-health'
        ]
        
        # Current inconsistent template pattern
        self.old_pattern = (
            r'(<example>\n\[CASE_1\]\n</example>\n\n'
            r'<questionnaire>\n\[questionnaire\]\n</questionnaire>\n\n)'
            r'(\[ROLE_PROMPTING\]\n\n)'
            r'(\[FORMAT_EXPLANATION\]\n\n)'
            r'(\[OUTPUT_INSTRUCTIONS\]\n\n)'
            r'(<task>\n\[question\]\n</task>)'
        )
        
        # New consistent template
        self.new_template = (
            r'\1'  # Keep <example> section
            r'<role>\n\2</role>\n\n'  # Wrap ROLE_PROMPTING with <role> tags
            r'<format>\n\3</format>\n\n'  # Wrap FORMAT_EXPLANATION with <format> tags  
            r'<output>\n\4</output>\n\n'  # Wrap OUTPUT_INSTRUCTIONS with <output> tags
            r'\5'  # Keep <task> section
        )
    
    def fix_prompt_template(self, prompt_template: str) -> str:
        """
        Fix a single prompt template by adding missing XML tags.
        
        Args:
            prompt_template: The original prompt template
            
        Returns:
            The fixed prompt template with XML tags added
        """
        # Apply the regex replacement to add XML tags
        fixed_template = re.sub(self.old_pattern, self.new_template, prompt_template)
        
        return fixed_template
    
    def process_json_file(self, json_file: Path) -> bool:
        """
        Process a single JSON file to fix prompt templates.
        
        Args:
            json_file: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Fix each case's prompt template
            fixed_count = 0
            for case in data:
                if 'prompt' in case:
                    original_prompt = case['prompt']
                    fixed_prompt = self.fix_prompt_template(original_prompt)
                    
                    if original_prompt != fixed_prompt:
                        case['prompt'] = fixed_prompt
                        fixed_count += 1
            
            # Write back the fixed data
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Fixed {fixed_count} prompt templates in {json_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {json_file}: {e}")
            return False
    
    def fix_all_datasets(self) -> None:
        """
        Fix all datasets that have inconsistent prompt templates.
        """
        if not self.advanced_prompts_dir.exists():
            logger.error(f"Advanced prompts directory {self.advanced_prompts_dir} does not exist")
            return
        
        logger.info("Fixing advanced_prompts consistency by adding missing XML tags")
        logger.info(f"Datasets to fix: {self.datasets_to_fix}")
        
        successful_fixes = []
        failed_fixes = []
        
        # Process each dataset that needs fixing
        for dataset in self.datasets_to_fix:
            dataset_dir = self.advanced_prompts_dir / dataset
            
            if not dataset_dir.exists():
                logger.warning(f"Dataset directory {dataset_dir} does not exist, skipping")
                continue
            
            logger.info(f"Processing dataset: {dataset}")
            
            # Process all JSON files in the dataset directory
            json_files = list(dataset_dir.glob("*.json"))
            for json_file in json_files:
                logger.info(f"  Processing: {json_file.name}")
                
                if self.process_json_file(json_file):
                    successful_fixes.append(f"{dataset}/{json_file.name}")
                else:
                    failed_fixes.append(f"{dataset}/{json_file.name}")
        
        # Summary
        logger.info("="*60)
        logger.info("ADVANCED_PROMPTS CONSISTENCY FIX SUMMARY")
        logger.info("="*60)
        
        if successful_fixes:
            logger.info(f"✅ Successfully fixed {len(successful_fixes)} files:")
            for file_path in successful_fixes[:10]:  # Show first 10
                logger.info(f"   - {file_path}")
            if len(successful_fixes) > 10:
                logger.info(f"   ... and {len(successful_fixes) - 10} more")
        
        if failed_fixes:
            logger.error(f"❌ Failed to fix {len(failed_fixes)} files:")
            for file_path in failed_fixes:
                logger.error(f"   - {file_path}")
        
        if not failed_fixes:
            logger.info("🎉 All advanced_prompts files fixed successfully!")
            logger.info("All datasets now have consistent XML tag format")

def main():
    """Main execution function."""
    fixer = AdvancedPromptsConsistencyFixer()
    fixer.fix_all_datasets()

if __name__ == "__main__":
    main()