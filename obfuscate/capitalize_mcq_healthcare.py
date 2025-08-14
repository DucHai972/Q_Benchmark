#!/usr/bin/env python3
"""
Healthcare MCQ Capitalization Script

This script capitalizes the MCQ column values in the healthcare dataset.
Target columns: Gender, Blood Type, Medical Condition, Insurance Provider, 
                Admission Type, Medication, Test Results

Usage:
    python capitalize_mcq_healthcare.py
"""

import csv
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def capitalize_mcq_columns(csv_file_path):
    """
    Capitalize MCQ column values in the healthcare dataset.
    
    Args:
        csv_file_path (Path): Path to the healthcare CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Processing MCQ columns in: {csv_file_path}")
    
    # Define the MCQ columns to capitalize
    mcq_columns = [
        'Gender',
        'Blood Type', 
        'Medical Condition',
        'Insurance Provider',
        'Admission Type',
        'Medication',
        'Test Results'
    ]
    
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
        
        # Find the indices of MCQ columns
        mcq_indices = {}
        for i, header in enumerate(headers):
            if header in mcq_columns:
                mcq_indices[header] = i
                logger.info(f"Found MCQ column '{header}' at index {i}")
        
        if not mcq_indices:
            logger.warning("No MCQ columns found to capitalize")
            return True
        
        # Capitalize the values in MCQ columns
        total_changes = 0
        column_changes = {col: 0 for col in mcq_indices.keys()}
        
        for row in rows:
            # Ensure row has enough columns
            while len(row) < len(headers):
                row.append("")
            
            for column_name, column_idx in mcq_indices.items():
                original_value = row[column_idx]
                if original_value and original_value.strip():
                    capitalized_value = original_value.upper()
                    if original_value != capitalized_value:
                        row[column_idx] = capitalized_value
                        column_changes[column_name] += 1
                        total_changes += 1
                        logger.debug(f"'{column_name}': '{original_value}' -> '{capitalized_value}'")
        
        logger.info(f"Total capitalization changes: {total_changes}")
        for column_name, count in column_changes.items():
            if count > 0:
                logger.info(f"  {column_name}: {count} changes")
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Successfully updated MCQ columns in {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def main():
    """Main function to capitalize MCQ columns."""
    logger.info("Starting MCQ column capitalization for healthcare dataset")
    
    csv_file_path = Path("preprocessed_data_csv/healthcare-dataset/healthcare_questionnaire.csv")
    
    if not csv_file_path.exists():
        logger.error(f"File not found: {csv_file_path}")
        return 1
    
    success = capitalize_mcq_columns(csv_file_path)
    
    if success:
        logger.info("Successfully capitalized MCQ columns!")
        return 0
    else:
        logger.error("Failed to capitalize MCQ columns")
        return 1


if __name__ == "__main__":
    exit(main())