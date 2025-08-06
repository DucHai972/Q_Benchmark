#!/usr/bin/env python3
"""
Convert All Formats Script

This script runs the advanced_prompt_converter for all available data formats
to generate converted prompts for XML, HTML, MD, TXT, and TTL formats
(JSON is already converted).
"""

import os
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_converter_for_format(data_format: str, max_cases: int = None):
    """
    Run the advanced prompt converter for a specific format.
    
    Args:
        data_format: The data format to convert (xml, html, md, txt, ttl)
        max_cases: Maximum number of cases to convert (None for all)
    """
    logger.info(f"Starting conversion for format: {data_format}")
    
    # Build the command
    cmd = [
        sys.executable, 
        "advanced_prompt_converter.py",
        "--all-datasets",
        "--format", data_format,
        "--output-format", "csv"
    ]
    
    if max_cases:
        cmd.extend(["--max-cases", str(max_cases)])
    
    try:
        # Run the converter
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully converted format: {data_format}")
        
        # Print output if verbose
        if result.stdout:
            logger.info(f"Converter output for {data_format}:\n{result.stdout}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting format {data_format}: {e}")
        if e.stdout:
            logger.error(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            logger.error(f"STDERR:\n{e.stderr}")
        raise

def main():
    """Main execution function."""
    
    # Check if advanced_prompt_converter.py exists
    converter_script = Path("advanced_prompt_converter.py")
    if not converter_script.exists():
        logger.error("advanced_prompt_converter.py not found in current directory")
        return 1
    
    # All formats to convert (excluding json which is already done)
    formats_to_convert = ["xml", "html", "md", "txt", "ttl"]
    
    logger.info(f"Converting prompts for formats: {', '.join(formats_to_convert)}")
    logger.info("This will generate CSV files for all datasets and tasks in each format")
    
    # Optional: limit cases for testing (set to None for full conversion)
    max_cases = None  # Set to a number like 10 for testing
    
    successful_conversions = []
    failed_conversions = []
    
    for data_format in formats_to_convert:
        try:
            run_converter_for_format(data_format, max_cases)
            successful_conversions.append(data_format)
        except Exception as e:
            logger.error(f"Failed to convert format {data_format}: {e}")
            failed_conversions.append(data_format)
    
    # Summary
    logger.info("="*60)
    logger.info("CONVERSION SUMMARY")
    logger.info("="*60)
    
    if successful_conversions:
        logger.info(f"✅ Successfully converted formats: {', '.join(successful_conversions)}")
    
    if failed_conversions:
        logger.error(f"❌ Failed to convert formats: {', '.join(failed_conversions)}")
        return 1
    
    logger.info("🎉 All format conversions completed successfully!")
    logger.info(f"📁 Check the 'converted_prompts' directory for output files")
    
    return 0

if __name__ == "__main__":
    exit(main())