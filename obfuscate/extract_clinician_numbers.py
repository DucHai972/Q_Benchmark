#!/usr/bin/env python3
"""
Extract Clinician Numbers for SUS-UTA7 Dataset

This script extracts the clinician numbers from the 'name' column (e.g., "Clinician 1" -> "1")
and fills the empty 'respondent' column with these numbers.

Usage:
    python extract_clinician_numbers.py
"""

import csv
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_clinician_number(name_value):
    """
    Extract number from clinician name.
    
    Args:
        name_value (str): Name like "Clinician 1", "Clinician 10", etc.
        
    Returns:
        str: The extracted number or empty string if not found
    """
    if not name_value:
        return ""
    
    # Use regex to extract number from "Clinician X" pattern
    match = re.search(r'Clinician\s+(\d+)', name_value, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return ""


def update_sus_uta7_respondent_column(csv_file_path):
    """
    Update the respondent column with clinician numbers.
    
    Args:
        csv_file_path (Path): Path to the SUS-UTA7 CSV file
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
        
        logger.info(f"Loaded {len(rows)} data rows")
        
        # Find the column indices
        respondent_idx = None
        name_idx = None
        
        for i, header in enumerate(headers):
            if header.lower() == 'respondent':
                respondent_idx = i
            elif header.lower() == 'name':
                name_idx = i
        
        if respondent_idx is None:
            logger.error("Could not find 'respondent' column")
            return False
        
        if name_idx is None:
            logger.error("Could not find 'name' column")
            return False
        
        logger.info(f"Found respondent column at index {respondent_idx}")
        logger.info(f"Found name column at index {name_idx}")
        
        # Update respondent column with extracted numbers
        updated_count = 0
        for row in rows:
            # Ensure row has enough columns
            while len(row) <= max(respondent_idx, name_idx):
                row.append("")
            
            # Extract clinician number from name column
            name_value = row[name_idx]
            clinician_number = extract_clinician_number(name_value)
            
            if clinician_number:
                row[respondent_idx] = clinician_number
                updated_count += 1
                logger.debug(f"Updated '{name_value}' -> respondent '{clinician_number}'")
        
        logger.info(f"Updated {updated_count} respondent entries")
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Successfully updated file: {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def main():
    """Main function to update the SUS-UTA7 file."""
    logger.info("Starting clinician number extraction for SUS-UTA7 dataset")
    
    csv_file_path = Path("preprocessed_data_csv/sus-uta7/sus_uta7_questionnaire.csv")
    
    if not csv_file_path.exists():
        logger.error(f"File not found: {csv_file_path}")
        return 1
    
    success = update_sus_uta7_respondent_column(csv_file_path)
    
    if success:
        logger.info("Successfully updated respondent column with clinician numbers!")
        return 0
    else:
        logger.error("Failed to update respondent column")
        return 1


if __name__ == "__main__":
    exit(main())