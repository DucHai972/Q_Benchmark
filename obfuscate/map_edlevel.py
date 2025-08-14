#!/usr/bin/env python3
"""
EdLevel Column Mapping Script

This script maps the EdLevel column content in the stack-overflow dataset 
from full text descriptions to MCQ option letters (A-I).

Mapping:
A. Primary/elementary school
B. Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)
C. Some college/university study without earning a degree
D. Associate degree (A.A., A.S., etc.)
E. Bachelor's degree (B.A., B.S., B.Eng., etc.)
F. Master's degree (M.A., M.S., M.Eng., MBA, etc.)
G. Professional degree (JD, MD, etc.)
H. Other doctoral degree (Ph.D., Ed.D., etc.)
I. Something else

Usage:
    python map_edlevel.py
"""

import csv
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_edlevel_mapping():
    """
    Create mapping dictionary from full text descriptions to MCQ option letters.
    
    Returns:
        dict: Mapping from text to letter codes
    """
    # Mapping based on the MCQ options provided
    mapping = {
        # Full text descriptions
        "Primary/elementary school": "A",
        "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)": "B",
        "Some college/university study without earning a degree": "C",
        "Associate degree (A.A., A.S., etc.)": "D",
        "Bachelor's degree (B.A., B.S., B.Eng., etc.)": "E",
        "Master's degree (M.A., M.S., M.Eng., MBA, etc.)": "F",
        "Professional degree (JD, MD, etc.)": "G",
        "Other doctoral degree (Ph.D., Ed.D., etc.)": "H",
        "Something else": "I",
        
        # Already mapped single letters (keep as-is)
        "A": "A",
        "B": "B", 
        "C": "C",
        "D": "D",
        "E": "E",
        "F": "F",
        "G": "G",
        "H": "H",
        "I": "I",
        
        # Handle variations with quotes and arrays
        "'A'": "A",
        "'B'": "B",
        "'C'": "C",
        "'D'": "D",
        "'E'": "E",
        "'F'": "F",
        "'G'": "G",
        "'H'": "H",
        "'I'": "I",
        
        # Handle array formats like ['A', 'C']
        "['A']": "A",
        "['B']": "B",
        "['C']": "C",
        "['D']": "D",
        "['E']": "E",
        "['F']": "F",
        "['G']": "G",
        "['H']": "H",
        "['I']": "I",
    }
    
    return mapping


def map_edlevel_value(value, mapping):
    """
    Map a single EdLevel value to its corresponding letter code.
    
    Args:
        value (str): The EdLevel value to map
        mapping (dict): The mapping dictionary
        
    Returns:
        str: The mapped letter code
    """
    if not value or value.strip() == "":
        return ""
    
    # Clean the value
    cleaned_value = value.strip()
    
    # Handle quoted strings
    if cleaned_value.startswith('"') and cleaned_value.endswith('"'):
        cleaned_value = cleaned_value[1:-1]
    
    # Try direct mapping first
    if cleaned_value in mapping:
        return mapping[cleaned_value]
    
    # Handle complex array formats like "'B']\"" or "'C']\"" 
    if "']" in cleaned_value:
        # Extract the letter between quotes
        import re
        match = re.search(r"'([A-I])'", cleaned_value)
        if match:
            letter = match.group(1)
            if letter in mapping:
                return mapping[letter]
    
    # Handle formats like "'C'"
    if cleaned_value.startswith("'") and cleaned_value.endswith("'") and len(cleaned_value) == 3:
        letter = cleaned_value[1]
        if letter in mapping:
            return mapping[letter]
    
    # Handle array-like formats
    if cleaned_value.startswith("['") and cleaned_value.endswith("']"):
        # Extract first value from array
        inner = cleaned_value[2:-2]
        if "'" in inner:
            first_option = inner.split("'")[0]
            if first_option in mapping:
                return mapping[first_option]
    
    # Handle cases where it might be a list with multiple values
    if cleaned_value.startswith("[") and cleaned_value.endswith("]"):
        # Take the first valid option
        inner = cleaned_value[1:-1]
        parts = inner.split(",")
        for part in parts:
            part = part.strip().strip("'\"")
            if part in mapping:
                return mapping[part]
    
    # Try partial matching for known descriptions
    for key, letter in mapping.items():
        if key in cleaned_value or cleaned_value in key:
            return letter
    
    logger.warning(f"Could not map EdLevel value: '{value}' -> keeping as-is")
    return cleaned_value


def map_edlevel_column(csv_file_path):
    """
    Map the EdLevel column in the stack-overflow CSV file.
    
    Args:
        csv_file_path (Path): Path to the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Processing EdLevel column in: {csv_file_path}")
    
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
        
        # Find the EdLevel column index
        edlevel_idx = None
        for i, header in enumerate(headers):
            if header.lower() == 'edlevel':
                edlevel_idx = i
                break
        
        if edlevel_idx is None:
            logger.error(f"Could not find 'EdLevel' column in {csv_file_path}")
            return False
        
        logger.info(f"Found EdLevel column at index {edlevel_idx}")
        
        # Create the mapping
        mapping = create_edlevel_mapping()
        
        # Map the EdLevel values
        mapped_count = 0
        unique_values = set()
        
        for row in rows:
            # Ensure row has enough columns
            while len(row) <= edlevel_idx:
                row.append("")
            
            original_value = row[edlevel_idx]
            mapped_value = map_edlevel_value(original_value, mapping)
            
            if original_value != mapped_value:
                mapped_count += 1
                logger.debug(f"Mapped '{original_value}' -> '{mapped_value}'")
            
            row[edlevel_idx] = mapped_value
            unique_values.add(mapped_value)
        
        logger.info(f"Mapped {mapped_count} EdLevel values")
        logger.info(f"Unique mapped values: {sorted(unique_values)}")
        
        # Write back to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Successfully updated EdLevel column in {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {csv_file_path}: {e}")
        return False


def main():
    """Main function to map EdLevel column."""
    logger.info("Starting EdLevel column mapping")
    
    csv_file_path = Path("preprocessed_data_csv/stack-overflow-2022-developer-survey/survey_results_sample.csv")
    
    if not csv_file_path.exists():
        logger.error(f"File not found: {csv_file_path}")
        return 1
    
    success = map_edlevel_column(csv_file_path)
    
    if success:
        logger.info("Successfully mapped EdLevel column to MCQ option letters!")
        return 0
    else:
        logger.error("Failed to map EdLevel column")
        return 1


if __name__ == "__main__":
    exit(main())