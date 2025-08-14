#!/usr/bin/env python3
"""
Column Cleanup Script

This script performs the following column manipulations:
1. Drop 'name' column from sus-uta7 dataset
2. Drop 'name' column from healthcare dataset  
3. Copy ResponseId to respondent column in stack-overflow dataset
4. Remove ResponseId column from stack-overflow dataset

Usage:
    python column_cleanup.py
"""

import csv
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def drop_column_from_csv(csv_file_path, column_to_drop):
    """
    Drop a specific column from a CSV file.
    
    Args:
        csv_file_path (Path): Path to the CSV file
        column_to_drop (str): Name of the column to drop
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Dropping column '{column_to_drop}' from {csv_file_path}")
    
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
        
        # Find the column index to drop
        column_idx = None
        for i, header in enumerate(headers):
            if header.lower() == column_to_drop.lower():
                column_idx = i
                break
        
        if column_idx is None:
            logger.warning(f"Column '{column_to_drop}' not found in {csv_file_path}")
            return False
        
        logger.info(f"Found column '{column_to_drop}' at index {column_idx}")
        
        # Remove the column from headers
        new_headers = headers[:column_idx] + headers[column_idx + 1:]
        
        # Remove the column from all rows
        new_rows = []
        for row in rows:
            # Ensure row has enough columns
            while len(row) <= column_idx:
                row.append("")
            new_row = row[:column_idx] + row[column_idx + 1:]
            new_rows.append(new_row)
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(new_headers)
            writer.writerows(new_rows)
        
        logger.info(f"Successfully dropped column '{column_to_drop}' from {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def copy_column_in_csv(csv_file_path, source_column, target_column):
    """
    Copy values from source column to target column in a CSV file.
    
    Args:
        csv_file_path (Path): Path to the CSV file
        source_column (str): Name of the source column
        target_column (str): Name of the target column
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Copying '{source_column}' to '{target_column}' in {csv_file_path}")
    
    try:
        # Read the CSV file
        rows = []
        headers = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                rows.append(row)
        
        logger.info(f"Loaded {len(rows)} data rows")
        
        # Find the column indices
        source_idx = None
        target_idx = None
        
        for i, header in enumerate(headers):
            if header.lower() == source_column.lower():
                source_idx = i
            elif header.lower() == target_column.lower():
                target_idx = i
        
        if source_idx is None:
            logger.error(f"Source column '{source_column}' not found")
            return False
        
        if target_idx is None:
            logger.error(f"Target column '{target_column}' not found")
            return False
        
        logger.info(f"Found source column '{source_column}' at index {source_idx}")
        logger.info(f"Found target column '{target_column}' at index {target_idx}")
        
        # Copy values from source to target column
        copied_count = 0
        for row in rows:
            # Ensure row has enough columns
            while len(row) <= max(source_idx, target_idx):
                row.append("")
            
            # Copy the value
            row[target_idx] = row[source_idx]
            copied_count += 1
        
        logger.info(f"Copied {copied_count} values from '{source_column}' to '{target_column}'")
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Successfully updated {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def main():
    """Main function to perform column cleanup operations."""
    logger.info("Starting column cleanup operations")
    
    success_count = 0
    total_operations = 4
    
    # 1. Drop 'name' column from sus-uta7 dataset
    sus_uta7_path = Path("preprocessed_data_csv/sus-uta7/sus_uta7_questionnaire.csv")
    if sus_uta7_path.exists():
        if drop_column_from_csv(sus_uta7_path, "name"):
            success_count += 1
        else:
            logger.error("Failed to drop 'name' column from sus-uta7 dataset")
    else:
        logger.error(f"File not found: {sus_uta7_path}")
    
    # 2. Drop 'name' column from healthcare dataset
    healthcare_path = Path("preprocessed_data_csv/healthcare-dataset/healthcare_questionnaire.csv")
    if healthcare_path.exists():
        if drop_column_from_csv(healthcare_path, "name"):
            success_count += 1
        else:
            logger.error("Failed to drop 'name' column from healthcare dataset")
    else:
        logger.error(f"File not found: {healthcare_path}")
    
    # 3. Copy ResponseId to respondent column in stack-overflow dataset
    stackoverflow_path = Path("preprocessed_data_csv/stack-overflow-2022-developer-survey/survey_results_sample.csv")
    if stackoverflow_path.exists():
        if copy_column_in_csv(stackoverflow_path, "ResponseId", "respondent"):
            success_count += 1
        else:
            logger.error("Failed to copy ResponseId to respondent column in stack-overflow dataset")
    else:
        logger.error(f"File not found: {stackoverflow_path}")
    
    # 4. Remove ResponseId column from stack-overflow dataset
    if stackoverflow_path.exists():
        if drop_column_from_csv(stackoverflow_path, "ResponseId"):
            success_count += 1
        else:
            logger.error("Failed to remove ResponseId column from stack-overflow dataset")
    
    logger.info(f"Completed {success_count}/{total_operations} operations successfully")
    
    if success_count == total_operations:
        logger.info("All column cleanup operations completed successfully!")
        return 0
    else:
        logger.error(f"Some operations failed ({total_operations - success_count} failures)")
        return 1


if __name__ == "__main__":
    exit(main())