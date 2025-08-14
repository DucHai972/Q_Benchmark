#!/usr/bin/env python3
"""
Overwrite Original Columns with Obfuscated Values Script

This script overwrites the original numeric columns in the main CSV files 
with their corresponding obfuscated values from the .numeric.obfuscated.csv files.

Usage:
    python overwrite_with_obfuscated.py [--test-mode]
"""

import csv
import re
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_numeric_or_date(value):
    """
    Check if a value is numeric or a date.
    
    Args:
        value (str): The value to check
        
    Returns:
        bool: True if numeric or date, False otherwise
    """
    if not value or value.strip() == "":
        return False
    
    # Check if it's a regular number
    try:
        float(value)
        return True
    except ValueError:
        pass
    
    # Check if it's a date (common formats)
    date_patterns = [
        r'^\d{4}-\d{1,2}-\d{1,2}$',  # YYYY-MM-DD
        r'^\d{1,2}/\d{1,2}/\d{4}$',  # MM/DD/YYYY or DD/MM/YYYY
        r'^\d{1,2}-\d{1,2}-\d{4}$',  # MM-DD-YYYY or DD-MM-YYYY
        r'^\d{4}/\d{1,2}/\d{1,2}$',  # YYYY/MM/DD
    ]
    
    for pattern in date_patterns:
        if re.match(pattern, value.strip()):
            return True
    
    return False


def overwrite_with_obfuscated(main_csv_path, obfuscated_csv_path, test_mode=False):
    """
    Overwrite numeric columns in the main CSV file with obfuscated values.
    
    Args:
        main_csv_path (Path): Path to the main CSV file
        obfuscated_csv_path (Path): Path to the obfuscated CSV file
        test_mode (bool): If True, only process first few rows for testing
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Overwriting numeric columns in: {main_csv_path}")
    
    try:
        # Read the main CSV file
        main_rows = []
        main_headers = []
        
        with open(main_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            main_headers = next(reader)
            for row in reader:
                main_rows.append(row)
                if test_mode and len(main_rows) >= 10:  # Only process first 10 rows in test mode
                    break
        
        # Read the obfuscated CSV file
        obfuscated_rows = []
        obfuscated_headers = []
        
        with open(obfuscated_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            obfuscated_headers = next(reader)
            for row in reader:
                obfuscated_rows.append(row)
                if test_mode and len(obfuscated_rows) >= 10:  # Match main CSV limit
                    break
        
        if test_mode:
            logger.info(f"Test mode: Processing {len(main_rows)} rows")
        else:
            logger.info(f"Processing {len(main_rows)} rows")
        
        # Find respondent column index in both files
        main_respondent_idx = None
        obfuscated_respondent_idx = None
        
        for i, header in enumerate(main_headers):
            if header.lower() == 'respondent':
                main_respondent_idx = i
                break
        
        for i, header in enumerate(obfuscated_headers):
            if header.lower() == 'respondent':
                obfuscated_respondent_idx = i
                break
        
        if main_respondent_idx is None or obfuscated_respondent_idx is None:
            logger.error("Could not find 'respondent' column in one or both files")
            return False
        
        # Create mapping from respondent ID to obfuscated row
        obfuscated_mapping = {}
        for row in obfuscated_rows:
            if obfuscated_respondent_idx < len(row):
                respondent_id = row[obfuscated_respondent_idx]
                obfuscated_mapping[respondent_id] = row
        
        # Identify numeric columns that exist in both files (excluding respondent)
        columns_to_overwrite = []
        
        # Find which columns from obfuscated file correspond to main file columns
        for main_idx, main_header in enumerate(main_headers):
            if main_idx == main_respondent_idx:
                continue
            
            # Check if this column exists in obfuscated file
            obfuscated_idx = None
            for obs_idx, obs_header in enumerate(obfuscated_headers):
                if obs_header == main_header:
                    obfuscated_idx = obs_idx
                    break
            
            if obfuscated_idx is not None:
                # Verify this is actually a numeric column by sampling values
                numeric_count = 0
                total_count = 0
                
                for row in main_rows:
                    if main_idx < len(row) and row[main_idx].strip():
                        total_count += 1
                        if is_numeric_or_date(row[main_idx]):
                            numeric_count += 1
                
                # Consider column numeric/date if >= 90% of non-empty values are numeric or date
                if total_count > 0 and numeric_count / total_count >= 0.9:
                    columns_to_overwrite.append((main_idx, main_header, obfuscated_idx))
                    logger.info(f"Will overwrite column: {main_header}")
        
        if not columns_to_overwrite:
            logger.warning("No matching numeric columns found between files")
            return False
        
        # Overwrite numeric columns with obfuscated values
        overwritten_count = 0
        for main_row in main_rows:
            # Ensure row has enough columns
            while len(main_row) < len(main_headers):
                main_row.append("")
            
            # Get respondent ID
            respondent_id = main_row[main_respondent_idx] if main_respondent_idx < len(main_row) else ""
            
            # Get corresponding obfuscated row
            obfuscated_row = obfuscated_mapping.get(respondent_id, [])
            
            if obfuscated_row:
                # Overwrite numeric columns with obfuscated values
                for main_idx, header_name, obfuscated_idx in columns_to_overwrite:
                    if obfuscated_idx < len(obfuscated_row):
                        old_value = main_row[main_idx]
                        new_value = obfuscated_row[obfuscated_idx]
                        main_row[main_idx] = new_value
                        
                        if old_value != new_value:
                            overwritten_count += 1
        
        # Write the updated CSV file
        with open(main_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(main_headers)
            writer.writerows(main_rows)
        
        logger.info(f"Successfully overwritten {len(columns_to_overwrite)} columns in {main_csv_path}")
        logger.info(f"Total values overwritten: {overwritten_count}")
        logger.info(f"Final file has {len(main_rows)} rows x {len(main_headers)} columns")
        
        # Log the overwritten columns
        for _, header, _ in columns_to_overwrite:
            logger.info(f"  Overwritten column: {header}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error overwriting columns for {main_csv_path}: {e}")
        return False


def find_csv_pairs(base_dir):
    """
    Find pairs of main CSV files and their corresponding obfuscated files.
    
    Args:
        base_dir (Path): Base directory to search
        
    Returns:
        list: List of (main_csv_path, obfuscated_csv_path) tuples
    """
    pairs = []
    
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            # Find main CSV files (not .numeric.csv or .obfuscated.csv)
            for csv_file in subdir.glob("*.csv"):
                if not (csv_file.name.endswith('.numeric.csv') or 
                       csv_file.name.endswith('.obfuscated.csv')):
                    
                    # Look for corresponding obfuscated file
                    base_name = csv_file.stem
                    obfuscated_name = f"{base_name}.numeric.obfuscated.csv"
                    obfuscated_path = subdir / obfuscated_name
                    
                    if obfuscated_path.exists():
                        pairs.append((csv_file, obfuscated_path))
                        logger.debug(f"Found pair: {csv_file.name} <-> {obfuscated_path.name}")
    
    return sorted(pairs)


def main():
    """Main function to overwrite numeric columns in all main CSV files."""
    parser = argparse.ArgumentParser(description='Overwrite original columns with obfuscated values')
    parser.add_argument('--test-mode', action='store_true', 
                       help='Test mode: process only first 10 rows of each file')
    args = parser.parse_args()
    
    if args.test_mode:
        logger.info("Running in TEST MODE - processing only first 10 rows per file")
    else:
        logger.info("Running in FULL MODE - processing all data")
    
    input_dir = Path("preprocessed_data_csv")
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return 1
    
    # Find all CSV file pairs
    csv_pairs = find_csv_pairs(input_dir)
    
    if not csv_pairs:
        logger.error("No CSV file pairs found")
        return 1
    
    logger.info(f"Found {len(csv_pairs)} CSV file pairs to process")
    
    success_count = 0
    
    # Process each CSV file pair
    for main_csv, obfuscated_csv in csv_pairs:
        if overwrite_with_obfuscated(main_csv, obfuscated_csv, test_mode=args.test_mode):
            success_count += 1
        else:
            logger.error(f"Failed to overwrite columns for {main_csv}")
    
    logger.info(f"Successfully processed {success_count}/{len(csv_pairs)} CSV file pairs")
    
    if success_count == len(csv_pairs):
        mode_str = "test" if args.test_mode else "full"
        logger.info(f"All overwrite operations completed successfully in {mode_str} mode!")
        return 0
    else:
        logger.error(f"Some operations failed ({len(csv_pairs) - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())