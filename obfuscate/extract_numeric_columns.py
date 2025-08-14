#!/usr/bin/env python3
"""
Simple Numeric Column Extractor

This script extracts the respondent column and numeric columns from each dataset,
then sorts the results by respondent. No ranking - just the original numeric values.

Usage:
    python extract_numeric_columns.py
"""

import csv
from pathlib import Path
import logging

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
    import re
    
    # Date patterns: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, etc.
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


def extract_numeric_columns(csv_file_path, output_dir):
    """
    Extract respondent and numeric columns from a CSV file.
    
    Args:
        csv_file_path (Path): Path to the CSV file
        output_dir (Path): Directory to save the extracted file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Processing: {csv_file_path}")
    
    try:
        # Read the CSV file
        rows = []
        headers = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                rows.append(row)
        
        logger.info(f"Loaded {len(rows)} rows and {len(headers)} columns")
        
        # Find respondent column
        respondent_idx = None
        for i, header in enumerate(headers):
            if header.lower() == 'respondent':
                respondent_idx = i
                break
        
        if respondent_idx is None:
            logger.error("Could not find 'respondent' column")
            return False
        
        # Identify numeric and date columns (excluding respondent)
        numeric_columns = []
        for i, header in enumerate(headers):
            if i == respondent_idx:
                continue  # Skip respondent column for numeric check
            
            # Check if column is numeric or date by sampling values
            numeric_count = 0
            total_count = 0
            
            for row in rows:
                if i < len(row) and row[i].strip():
                    total_count += 1
                    if is_numeric_or_date(row[i]):
                        numeric_count += 1
            
            # Consider column numeric/date if >= 90% of non-empty values are numeric or date
            if total_count > 0 and numeric_count / total_count >= 0.9:
                numeric_columns.append((i, header))
                logger.info(f"  Including numeric/date column: {header} ({numeric_count}/{total_count} = {numeric_count/total_count*100:.1f}% numeric/date)")
            else:
                logger.info(f"  Excluding non-numeric column: {header}")
        
        if not numeric_columns:
            logger.warning("No numeric/date columns found")
            return True
        
        # Create output headers: respondent + numeric/date columns
        output_headers = ['respondent'] + [header for _, header in numeric_columns]
        output_indices = [respondent_idx] + [idx for idx, _ in numeric_columns]
        
        # Extract data and sort by respondent
        output_rows = []
        for row in rows:
            # Ensure row has enough columns
            while len(row) < len(headers):
                row.append("")
            
            output_row = []
            for idx in output_indices:
                output_row.append(row[idx])
            output_rows.append(output_row)
        
        # Sort by respondent (convert to int for proper numeric sorting)
        def sort_key(row):
            try:
                return int(row[0]) if row[0] else 0
            except ValueError:
                return 0
        
        output_rows.sort(key=sort_key)
        
        # Generate output filename
        input_filename = csv_file_path.stem
        output_filename = f"{input_filename}.numeric.csv"
        output_path = output_dir / output_filename
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write output file
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(output_headers)
            writer.writerows(output_rows)
        
        logger.info(f"Saved numeric/date columns to: {output_path}")
        logger.info(f"Output shape: {len(output_rows)} rows x {len(output_headers)} columns")
        
        # Log column summary
        for header in output_headers:
            logger.info(f"  Column: {header}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing {csv_file_path}: {e}")
        return False


def find_csv_files(base_dir):
    """
    Find all main CSV files (not .rankings.csv or .numeric.csv files).
    
    Args:
        base_dir (Path): Base directory to search
        
    Returns:
        list: List of CSV file paths
    """
    csv_files = []
    
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            for csv_file in subdir.glob("*.csv"):
                # Skip already processed files
                if not (csv_file.name.endswith('.rankings.csv') or 
                       csv_file.name.endswith('.numeric.csv')):
                    csv_files.append(csv_file)
    
    return sorted(csv_files)


def main():
    """Main function to extract numeric and date columns from all datasets."""
    logger.info("Starting numeric and date column extraction")
    
    input_dir = Path("preprocessed_data_csv")
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return 1
    
    # Find all CSV files
    csv_files = find_csv_files(input_dir)
    
    if not csv_files:
        logger.error("No CSV files found")
        return 1
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    success_count = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        # Output to the same directory as the input file
        output_dir = csv_file.parent
        
        if extract_numeric_columns(csv_file, output_dir):
            success_count += 1
        else:
            logger.error(f"Failed to process {csv_file}")
    
    logger.info(f"Successfully processed {success_count}/{len(csv_files)} CSV files")
    
    if success_count == len(csv_files):
        logger.info("All numeric and date column extractions completed successfully!")
        return 0
    else:
        logger.error(f"Some operations failed ({len(csv_files) - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())