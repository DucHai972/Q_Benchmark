#!/usr/bin/env python3
"""
Merge Obfuscated Columns Script

This script merges obfuscated numeric columns back into the main CSV files.
For each numeric column, it adds a corresponding "_obfuscated" column with 
the rank-swapped values.

Usage:
    python merge_obfuscated_columns.py [--test-mode]
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


def merge_obfuscated_columns(main_csv_path, obfuscated_csv_path, test_mode=False):
    """
    Merge obfuscated columns into the main CSV file.
    
    Args:
        main_csv_path (Path): Path to the main CSV file
        obfuscated_csv_path (Path): Path to the obfuscated CSV file
        test_mode (bool): If True, only process first few rows for testing
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Merging obfuscated columns into: {main_csv_path}")
    
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
        numeric_column_pairs = []
        
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
                    numeric_column_pairs.append((main_idx, main_header, obfuscated_idx))
                    logger.info(f"Will add obfuscated column for: {main_header}")
        
        if not numeric_column_pairs:
            logger.warning("No matching numeric columns found between files")
            return False
        
        # Create new headers by adding "_obfuscated" versions
        new_headers = main_headers[:]
        obfuscated_header_positions = []
        
        for main_idx, header_name, _ in numeric_column_pairs:
            obfuscated_header = f"{header_name}_obfuscated"
            # Insert the obfuscated column right after the original column
            insert_position = main_idx + 1 + len([pos for pos in obfuscated_header_positions if pos <= main_idx])
            new_headers.insert(insert_position, obfuscated_header)
            obfuscated_header_positions.append(main_idx)
        
        # Create new rows with obfuscated columns
        new_rows = []
        for main_row in main_rows:
            # Ensure row has enough columns
            while len(main_row) < len(main_headers):
                main_row.append("")
            
            # Get respondent ID
            respondent_id = main_row[main_respondent_idx] if main_respondent_idx < len(main_row) else ""
            
            # Get corresponding obfuscated row
            obfuscated_row = obfuscated_mapping.get(respondent_id, [])
            
            # Build new row with obfuscated columns inserted
            new_row = []
            obfuscated_cols_added = 0
            
            for i, value in enumerate(main_row):
                new_row.append(value)
                
                # Check if we need to add an obfuscated column after this position
                for main_idx, header_name, obfuscated_idx in numeric_column_pairs:
                    if i == main_idx:
                        # Add obfuscated value
                        if obfuscated_idx < len(obfuscated_row):
                            obfuscated_value = obfuscated_row[obfuscated_idx]
                        else:
                            obfuscated_value = ""
                        new_row.append(obfuscated_value)
                        obfuscated_cols_added += 1
            
            new_rows.append(new_row)
        
        # Write the merged CSV file
        with open(main_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(new_headers)
            writer.writerows(new_rows)
        
        logger.info(f"Successfully merged {len(numeric_column_pairs)} obfuscated columns into {main_csv_path}")
        logger.info(f"New file has {len(new_rows)} rows x {len(new_headers)} columns")
        
        # Log the new column structure
        for header in new_headers:
            if header.endswith('_obfuscated'):
                logger.info(f"  Added obfuscated column: {header}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error merging obfuscated columns for {main_csv_path}: {e}")
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
    """Main function to merge obfuscated columns into all main CSV files."""
    parser = argparse.ArgumentParser(description='Merge obfuscated columns into main CSV files')
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
        if merge_obfuscated_columns(main_csv, obfuscated_csv, test_mode=args.test_mode):
            success_count += 1
        else:
            logger.error(f"Failed to merge obfuscated columns for {main_csv}")
    
    logger.info(f"Successfully merged {success_count}/{len(csv_pairs)} CSV file pairs")
    
    if success_count == len(csv_pairs):
        mode_str = "test" if args.test_mode else "full"
        logger.info(f"All merge operations completed successfully in {mode_str} mode!")
        return 0
    else:
        logger.error(f"Some operations failed ({len(csv_pairs) - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())