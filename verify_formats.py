#!/usr/bin/env python3
"""
Verify All Formats Conversion

This script verifies that converted prompts were generated for all 6 data formats
across all datasets and tasks.
"""

import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_conversions():
    """Verify that all formats have been converted."""
    
    converted_prompts_dir = Path("converted_prompts")
    if not converted_prompts_dir.exists():
        logger.error("converted_prompts directory not found")
        return False
    
    # Expected formats
    expected_formats = ["json", "xml", "html", "md", "txt", "ttl"]
    
    # Get all datasets
    datasets = [d.name for d in converted_prompts_dir.iterdir() if d.is_dir()]
    
    logger.info(f"Found datasets: {', '.join(datasets)}")
    
    total_expected = 0
    total_found = 0
    missing_files = []
    
    for dataset in datasets:
        dataset_dir = converted_prompts_dir / dataset
        
        # Get all tasks for this dataset
        tasks = [t.name for t in dataset_dir.iterdir() if t.is_dir()]
        
        for task in tasks:
            task_dir = dataset_dir / task
            
            # Check each format
            for format_name in expected_formats:
                expected_file = task_dir / f"{task}_{format_name}_converted_prompts.csv"
                total_expected += 1
                
                if expected_file.exists():
                    total_found += 1
                    logger.debug(f"✅ Found: {expected_file}")
                else:
                    missing_files.append(str(expected_file))
                    logger.warning(f"❌ Missing: {expected_file}")
    
    # Summary
    logger.info("="*60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total expected files: {total_expected}")
    logger.info(f"Total found files: {total_found}")
    logger.info(f"Missing files: {len(missing_files)}")
    
    if missing_files:
        logger.error("Missing files:")
        for missing_file in missing_files:
            logger.error(f"  - {missing_file}")
        return False
    else:
        logger.info("🎉 All format conversions verified successfully!")
        
        # Show breakdown by format
        format_counts = {}
        for dataset in datasets:
            dataset_dir = converted_prompts_dir / dataset
            tasks = [t.name for t in dataset_dir.iterdir() if t.is_dir()]
            
            for format_name in expected_formats:
                if format_name not in format_counts:
                    format_counts[format_name] = 0
                format_counts[format_name] += len(tasks)
        
        logger.info("Files per format:")
        for format_name, count in format_counts.items():
            logger.info(f"  - {format_name.upper()}: {count} files")
        
        return True

def main():
    """Main execution function."""
    
    logger.info("Verifying converted prompt files for all formats...")
    
    success = verify_conversions()
    
    if success:
        logger.info("✅ Verification completed successfully!")
        return 0
    else:
        logger.error("❌ Verification failed!")
        return 1

if __name__ == "__main__":
    exit(main())