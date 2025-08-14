#!/usr/bin/env python3
"""
Data Obfuscation Script using Rank Swapping

This script implements rank swapping obfuscation for numeric columns in CSV files.
For each numeric variable X: sort by value; for each record at rank r, 
choose a swap partner uniformly in [r-w, r+w] (window w ≈ 2.5% of n).

Usage:
    python obfuscate_data.py [--test-mode]
"""

import csv
import random
import math
from pathlib import Path
import logging
from datetime import datetime
import argparse
import re

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


def convert_to_numeric(value):
    """
    Convert a value to numeric for sorting/ranking.
    
    Args:
        value (str): The value to convert
        
    Returns:
        float: Numeric representation of the value
    """
    if not value or value.strip() == "":
        return float('inf')  # Put empty values at the end
    
    # Try regular number first
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try to parse as date and convert to days since epoch
    date_patterns = [
        (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', '%Y-%m-%d'),  # YYYY-MM-DD
        (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', '%m/%d/%Y'),  # MM/DD/YYYY
        (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', '%m-%d-%Y'),  # MM-DD-YYYY
        (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', '%Y/%m/%d'),  # YYYY/MM/DD
    ]
    
    for pattern, date_format in date_patterns:
        if re.match(pattern, value.strip()):
            try:
                dt = datetime.strptime(value.strip(), date_format)
                # Convert to days since Unix epoch
                epoch = datetime(1970, 1, 1)
                return (dt - epoch).days
            except ValueError:
                continue
    
    # If we can't convert, return a large number to put it at the end
    return float('inf')


def rank_swap_column(values, respondent_ids, window_ratio=0.025, random_seed=42):
    """
    Apply rank swapping to a single column of values.
    
    Args:
        values (list): List of values to obfuscate
        respondent_ids (list): Corresponding respondent IDs
        window_ratio (float): Window size as ratio of total records (default: 2.5%)
        random_seed (int): Random seed for reproducibility
        
    Returns:
        dict: Mapping from respondent_id to obfuscated value
    """
    random.seed(random_seed)
    
    n = len(values)
    if n == 0:
        return {}
    
    # Calculate window size (at least 1)
    window_size = max(1, math.ceil(window_ratio * n))
    logger.debug(f"Window size: {window_size} (ratio: {window_ratio}, n: {n})")
    
    # Create list of (numeric_value, original_value, respondent_id, index) tuples
    value_tuples = []
    for i, (val, resp_id) in enumerate(zip(values, respondent_ids)):
        numeric_val = convert_to_numeric(val)
        value_tuples.append((numeric_val, val, resp_id, i))
    
    # Sort by numeric value to get ranks
    value_tuples.sort(key=lambda x: x[0])
    
    # Create a copy for swapping
    swapped_values = [item[1] for item in value_tuples]  # original values in rank order
    
    # Perform rank swapping
    swaps_performed = 0
    for rank in range(n):
        # Calculate swap window [max(0, rank-w), min(n-1, rank+w)]
        min_rank = max(0, rank - window_size)
        max_rank = min(n - 1, rank + window_size)
        
        # Choose random swap partner within window
        swap_partner = random.randint(min_rank, max_rank)
        
        if swap_partner != rank:
            # Swap values
            swapped_values[rank], swapped_values[swap_partner] = \
                swapped_values[swap_partner], swapped_values[rank]
            swaps_performed += 1
    
    logger.debug(f"Performed {swaps_performed} swaps out of {n} possible positions")
    
    # Create mapping from respondent_id to obfuscated value
    result = {}
    for i, (_, _, resp_id, _) in enumerate(value_tuples):
        result[resp_id] = swapped_values[i]
    
    return result


def obfuscate_csv_file(input_path, output_path, test_mode=False, random_seed=42):
    """
    Obfuscate numeric columns in a CSV file using rank swapping.
    
    Args:
        input_path (Path): Path to input CSV file
        output_path (Path): Path to output obfuscated CSV file
        test_mode (bool): If True, only process first few rows for testing
        random_seed (int): Random seed for reproducibility
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Obfuscating: {input_path}")
    
    try:
        # Read the CSV file
        rows = []
        headers = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                rows.append(row)
                if test_mode and len(rows) >= 10:  # Only process first 10 rows in test mode
                    break
        
        if test_mode:
            logger.info(f"Test mode: Processing {len(rows)} rows (first 10)")
        else:
            logger.info(f"Processing {len(rows)} rows")
        
        if len(rows) == 0:
            logger.warning("No data rows found")
            return False
        
        # Find respondent column
        respondent_idx = None
        for i, header in enumerate(headers):
            if header.lower() == 'respondent':
                respondent_idx = i
                break
        
        if respondent_idx is None:
            logger.error("Could not find 'respondent' column")
            return False
        
        # Extract respondent IDs
        respondent_ids = []
        for row in rows:
            if respondent_idx < len(row):
                respondent_ids.append(row[respondent_idx])
            else:
                respondent_ids.append("")
        
        # Identify numeric columns (excluding respondent)
        numeric_column_indices = []
        for i, header in enumerate(headers):
            if i == respondent_idx:
                continue
            
            # Check if column contains numeric or date values
            numeric_count = 0
            total_count = 0
            
            for row in rows:
                if i < len(row) and row[i].strip():
                    total_count += 1
                    if is_numeric_or_date(row[i]):
                        numeric_count += 1
            
            # Consider column numeric if >= 90% of non-empty values are numeric/date
            if total_count > 0 and numeric_count / total_count >= 0.9:
                numeric_column_indices.append((i, header))
                logger.info(f"Will obfuscate column: {header}")
        
        if not numeric_column_indices:
            logger.warning("No numeric columns found to obfuscate")
            return False
        
        # Create obfuscated data by copying original
        obfuscated_rows = [row[:] for row in rows]  # Deep copy
        
        # Apply rank swapping to each numeric column
        for col_idx, col_name in numeric_column_indices:
            logger.info(f"Obfuscating column: {col_name}")
            
            # Extract column values
            column_values = []
            for row in rows:
                if col_idx < len(row):
                    column_values.append(row[col_idx])
                else:
                    column_values.append("")
            
            # Apply rank swapping
            obfuscated_mapping = rank_swap_column(column_values, respondent_ids, 
                                                random_seed=random_seed + col_idx)
            
            # Update obfuscated rows
            for i, resp_id in enumerate(respondent_ids):
                if resp_id in obfuscated_mapping:
                    obfuscated_rows[i][col_idx] = obfuscated_mapping[resp_id]
        
        # Write obfuscated data
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(obfuscated_rows)
        
        logger.info(f"Saved obfuscated data to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error obfuscating {input_path}: {e}")
        return False


def find_numeric_csv_files(base_dir):
    """
    Find all .numeric.csv files.
    
    Args:
        base_dir (Path): Base directory to search
        
    Returns:
        list: List of .numeric.csv file paths
    """
    csv_files = []
    
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            for csv_file in subdir.glob("*.numeric.csv"):
                csv_files.append(csv_file)
    
    return sorted(csv_files)


def main():
    """Main function to obfuscate numeric columns in all datasets."""
    parser = argparse.ArgumentParser(description='Obfuscate numeric data using rank swapping')
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
    
    # Find all .numeric.csv files
    csv_files = find_numeric_csv_files(input_dir)
    
    if not csv_files:
        logger.error("No .numeric.csv files found")
        return 1
    
    logger.info(f"Found {len(csv_files)} .numeric.csv files to process")
    
    success_count = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        # Generate output filename
        output_filename = csv_file.stem.replace('.numeric', '.numeric.obfuscated') + '.csv'
        output_path = csv_file.parent / output_filename
        
        if obfuscate_csv_file(csv_file, output_path, test_mode=args.test_mode):
            success_count += 1
        else:
            logger.error(f"Failed to obfuscate {csv_file}")
    
    logger.info(f"Successfully obfuscated {success_count}/{len(csv_files)} CSV files")
    
    if success_count == len(csv_files):
        mode_str = "test" if args.test_mode else "full"
        logger.info(f"All obfuscation operations completed successfully in {mode_str} mode!")
        return 0
    else:
        logger.error(f"Some operations failed ({len(csv_files) - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())