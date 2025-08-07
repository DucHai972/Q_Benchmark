#!/usr/bin/env python3
"""
Convert prompts to wo_change_order variant

This script processes all converted prompts in the converted_prompts directory
and creates variants with changed section order by moving the '<questionnaire>...</questionnaire>' 
section to the end of the prompt (after the '</task>' section).
"""

import os
import csv
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WoChangeOrderConverter:
    def __init__(self, 
                 input_dir: str = "converted_prompts",
                 output_dir: str = "converted_prompts_variants/wo_change_order"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def change_prompt_order(self, prompt: str) -> str:
        """
        Move the <questionnaire>...</questionnaire> section to the end of the prompt.
        
        Args:
            prompt: The original prompt text
            
        Returns:
            The prompt with questionnaire section moved to the end
        """
        # Find the questionnaire section
        questionnaire_match = re.search(r'<questionnaire>(.*?)</questionnaire>', prompt, re.DOTALL)
        
        if not questionnaire_match:
            # If no questionnaire section found, return original prompt
            return prompt
        
        # Extract the questionnaire section
        questionnaire_section = questionnaire_match.group(0)
        
        # Remove the questionnaire section from its current position
        prompt_without_questionnaire = re.sub(r'<questionnaire>.*?</questionnaire>\s*', '', prompt, flags=re.DOTALL)
        
        # Add the questionnaire section to the end
        modified_prompt = prompt_without_questionnaire.rstrip() + '\n\n' + questionnaire_section
        
        # Clean up any excessive whitespace
        modified_prompt = re.sub(r'\n\s*\n\s*\n+', '\n\n', modified_prompt)
        modified_prompt = modified_prompt.strip()
        
        return modified_prompt
    
    def process_csv_file(self, input_file: Path, output_file: Path) -> bool:
        """
        Process a single CSV file to change the order of sections in prompts.
        
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
                        modified_prompt = self.change_prompt_order(original_prompt)
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
        logger.info("Moving <questionnaire>...</questionnaire> sections to the end of prompts")
        
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
        logger.info("WO_CHANGE_ORDER CONVERSION SUMMARY")
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
    converter = WoChangeOrderConverter()
    converter.convert_all_prompts()

if __name__ == "__main__":
    main()