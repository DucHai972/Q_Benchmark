#!/usr/bin/env python3
"""
Shuffle and Sort Script

This script performs the following operations on all CSV files:
1. Shuffle the respondent column values randomly across all rows
2. Sort the CSV files by the respondent column

Usage:
    python shuffle_and_sort.py
"""

import csv
import random
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def shuffle_respondent_and_sort_csv(csv_file_path):
    """
    Shuffle respondent column values and sort the CSV by respondent column.
    
    Args:
        csv_file_path (Path): Path to the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Processing file: {csv_file_path}")
    
    try:
        # Read the CSV file
        rows = []
        headers = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                rows.append(row)
        
        logger.info(f"Loaded {len(rows)} data rows with headers: {headers}")
        
        # Find the respondent column index (try 'respondent' first, then 'ResponseId')
        respondent_idx = None
        respondent_column_name = None
        
        for i, header in enumerate(headers):
            if header.lower() == 'respondent':
                respondent_idx = i
                respondent_column_name = header
                break
            elif header.lower() == 'responseid':
                respondent_idx = i
                respondent_column_name = header
                break
        
        if respondent_idx is None:
            logger.warning(f"Could not find 'respondent' or 'ResponseId' column in {csv_file_path} - skipping")
            return True  # Skip files without respondent columns instead of failing
        
        logger.info(f"Found {respondent_column_name} column at index {respondent_idx}")
        
        # Extract all respondent values
        respondent_values = []
        for row in rows:
            # Ensure row has enough columns
            while len(row) <= respondent_idx:
                row.append("")
            respondent_values.append(row[respondent_idx])
        
        # Shuffle the respondent values
        shuffled_values = respondent_values.copy()
        random.shuffle(shuffled_values)
        
        logger.info(f"Shuffled {len(shuffled_values)} respondent values")
        
        # Assign shuffled values back to rows
        for i, row in enumerate(rows):
            row[respondent_idx] = shuffled_values[i]
        
        # Sort rows by respondent column (convert to int for proper numeric sorting)
        def sort_key(row):
            try:
                # Try to convert to int for numeric sorting
                return int(row[respondent_idx]) if row[respondent_idx] else 0
            except (ValueError, IndexError):
                # If conversion fails, use string sorting
                return str(row[respondent_idx]) if len(row) > respondent_idx else ""
        
        rows.sort(key=sort_key)
        
        logger.info(f"Sorted rows by respondent column")
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Successfully processed {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def find_all_csv_files(base_dir):
    """
    Find all CSV files in the preprocessed_data_csv directory.
    
    Args:
        base_dir (Path): Base directory to search
        
    Returns:
        list: List of CSV file paths
    """
    csv_files = []
    
    # Look for CSV files in subdirectories
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            for csv_file in subdir.glob("*.csv"):
                csv_files.append(csv_file)
    
    return csv_files


def main():
    """Main function to shuffle and sort all CSV files."""
    logger.info("Starting shuffle and sort operations for all CSV files")
    
    # Set random seed for reproducibility (you can comment this out for true randomness)
    random.seed(42)
    logger.info("Set random seed to 42 for reproducible results")
    
    base_dir = Path("preprocessed_data_csv")
    
    if not base_dir.exists():
        logger.error(f"Directory not found: {base_dir}")
        return 1
    
    # Find all CSV files
    csv_files = find_all_csv_files(base_dir)
    
    if not csv_files:
        logger.error("No CSV files found in preprocessed_data_csv subdirectories")
        return 1
    
    logger.info(f"Found {len(csv_files)} CSV files to process:")
    for csv_file in csv_files:
        logger.info(f"  - {csv_file}")
    
    success_count = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        if shuffle_respondent_and_sort_csv(csv_file):
            success_count += 1
        else:
            logger.error(f"Failed to process {csv_file}")
    
    logger.info(f"Successfully processed {success_count}/{len(csv_files)} CSV files")
    
    if success_count == len(csv_files):
        logger.info("All shuffle and sort operations completed successfully!")
        return 0
    else:
        logger.error(f"Some operations failed ({len(csv_files) - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())