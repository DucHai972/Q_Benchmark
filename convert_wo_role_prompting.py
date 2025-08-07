#!/usr/bin/env python3
"""
Convert prompts to wo_role_prompting variant

This script processes all converted prompts in the converted_prompts directory
and creates variants without role prompting by removing the '<role> ... </role>' sections.
"""

import os
import csv
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WoRolePromptingConverter:
    def __init__(self, 
                 input_dir: str = "converted_prompts",
                 output_dir: str = "converted_prompts_variants/wo_role_prompting"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def remove_role_prompting(self, prompt: str) -> str:
        """
        Remove the <role>...</role> section from a prompt.
        
        Args:
            prompt: The original prompt text
            
        Returns:
            The prompt with role prompting section removed
        """
        # Pattern to match <role>...</role> section (including any content inside)
        role_pattern = r'<role>\s*.*?\s*</role>\s*'
        
        # Remove the role section
        modified_prompt = re.sub(role_pattern, '', prompt, flags=re.DOTALL)
        
        # Clean up extra whitespace and newlines that might be left
        modified_prompt = re.sub(r'\n\s*\n\s*\n', '\n\n', modified_prompt)
        modified_prompt = modified_prompt.strip()
        
        return modified_prompt
    
    def process_csv_file(self, input_file: Path, output_file: Path) -> bool:
        """
        Process a single CSV file to remove role prompting from prompts.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(input_file, 'r', encoding='utf-8') as infile, \
                 open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                processed_count = 0
                for row in reader:
                    # Process the prompt column
                    if 'prompt' in row and row['prompt']:
                        original_prompt = row['prompt']
                        modified_prompt = self.remove_role_prompting(original_prompt)
                        row['prompt'] = modified_prompt
                        processed_count += 1
                    
                    writer.writerow(row)
                
                logger.info(f"Processed {processed_count} prompts in {input_file.name}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            return False
    
    def convert_all_prompts(self) -> None:
        """
        Convert all CSV files in the converted_prompts directory.
        """
        if not self.input_dir.exists():
            logger.error(f"Input directory {self.input_dir} does not exist")
            return
            
        logger.info(f"Converting prompts from {self.input_dir} to {self.output_dir}")
        logger.info("Removing <role>...</role> sections from all prompts")
        
        successful_conversions = []
        failed_conversions = []
        
        # Walk through all CSV files in the input directory
        for csv_file in self.input_dir.rglob("*.csv"):
            # Calculate relative path for output structure
            relative_path = csv_file.relative_to(self.input_dir)
            output_file = self.output_dir / relative_path
            
            logger.info(f"Processing: {relative_path}")
            
            if self.process_csv_file(csv_file, output_file):
                successful_conversions.append(str(relative_path))
            else:
                failed_conversions.append(str(relative_path))
        
        # Summary
        logger.info("="*60)
        logger.info("WO_ROLE_PROMPTING CONVERSION SUMMARY")
        logger.info("="*60)
        
        if successful_conversions:
            logger.info(f"✅ Successfully converted {len(successful_conversions)} files:")
            for file_path in successful_conversions[:5]:  # Show first 5
                logger.info(f"   - {file_path}")
            if len(successful_conversions) > 5:
                logger.info(f"   ... and {len(successful_conversions) - 5} more")
        
        if failed_conversions:
            logger.error(f"❌ Failed to convert {len(failed_conversions)} files:")
            for file_path in failed_conversions:
                logger.error(f"   - {file_path}")
        
        if not failed_conversions:
            logger.info("🎉 All prompt conversions completed successfully!")
            logger.info(f"📁 Check the '{self.output_dir}' directory for output files")

def main():
    """Main execution function."""
    converter = WoRolePromptingConverter()
    converter.convert_all_prompts()

if __name__ == "__main__":
    main()