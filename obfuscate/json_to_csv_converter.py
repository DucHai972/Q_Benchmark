#!/usr/bin/env python3
"""
JSON to CSV Converter for Q_Benchmark Preprocessed Data

This script converts the JSON files in preprocessed_data/ to CSV format,
creating respondent-based CSV files where each row is a respondent and
each column is an attribute.

Usage:
    python json_to_csv_converter.py
"""

import os
import json
import csv
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_json_data(json_file_path):
    """
    Load JSON data from file.
    
    Args:
        json_file_path (str): Path to the JSON file
        
    Returns:
        dict: Parsed JSON data or None if error
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error loading JSON file {json_file_path}: {e}")
        return None


def extract_respondent_data(json_data):
    """
    Extract respondent data from JSON structure and convert to CSV format.
    Preserves the original column order from the JSON questions section.
    
    Args:
        json_data (dict): JSON data with 'questions' and 'responses' sections
        
    Returns:
        tuple: (headers, rows) where headers is list of column names and 
               rows is list of lists containing respondent data
    """
    if not json_data or 'responses' not in json_data:
        logger.error("Invalid JSON structure - missing 'responses' section")
        return [], []
    
    responses = json_data['responses']
    if not responses:
        logger.warning("No responses found in JSON data")
        return [], []
    
    # Build headers in original order
    headers = ['respondent']  # Always start with respondent
    
    # If questions section exists, use that order for the main attributes
    if 'questions' in json_data:
        questions_data = json_data['questions']
        if isinstance(questions_data, dict):
            # Questions as dictionary (like healthcare dataset)
            questions_order = list(questions_data.keys())
            headers.extend(questions_order)
        elif isinstance(questions_data, list):
            # Questions as list (like stack-overflow dataset)
            # Extract field names from list items (format: "FieldName: Description")
            for question_item in questions_data:
                if isinstance(question_item, str) and ':' in question_item:
                    field_name = question_item.split(':')[0].strip()
                    headers.append(field_name)
                else:
                    # Fallback: use the item as-is if it doesn't match expected format
                    headers.append(str(question_item))
        else:
            logger.warning(f"Unexpected 'questions' format: {type(questions_data)}")
    
    # If no questions section or fallback needed, collect from first response
    if len(headers) == 1:  # Only 'respondent' so far
        if responses:
            first_response = responses[0]
            if 'answers' in first_response:
                headers.extend(first_response['answers'].keys())
            # Add direct attributes (excluding 'respondent' and 'answers')
            for key in first_response.keys():
                if key not in ['respondent', 'answers'] and key not in headers:
                    headers.append(key)
    
    # Collect any additional attributes not in questions (for datasets with extra fields)
    additional_attrs = set()
    for response in responses:
        # Check answers section
        if 'answers' in response:
            for key in response['answers'].keys():
                if key not in headers:
                    additional_attrs.add(key)
        
        # Check direct attributes
        for key in response.keys():
            if key not in ['answers'] and key not in headers:
                additional_attrs.add(key)
    
    # Add additional attributes at the end (sorted for consistency)
    if additional_attrs:
        headers.extend(sorted(additional_attrs))
    
    # Second pass: extract data for each respondent
    rows = []
    for response in responses:
        row = {}
        
        # Initialize all columns with empty strings
        for header in headers:
            row[header] = ''
        
        # Fill in respondent ID
        if 'respondent' in response:
            row['respondent'] = str(response['respondent'])
        
        # Fill in answers if they exist
        if 'answers' in response:
            for key, value in response['answers'].items():
                if key in row:
                    row[key] = str(value) if value is not None else ''
        
        # Fill in direct attributes
        for key, value in response.items():
            if key not in ['answers'] and key in row:
                row[key] = str(value) if value is not None else ''
        
        # Convert to list in header order
        row_list = [row[header] for header in headers]
        rows.append(row_list)
    
    return headers, rows


def save_csv_file(headers, rows, output_file_path):
    """
    Save headers and rows to CSV file.
    
    Args:
        headers (list): Column headers
        rows (list): List of lists containing row data
        output_file_path (str): Path to save CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Saved CSV with {len(rows)} respondents and {len(headers)} columns: {output_file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving CSV file {output_file_path}: {e}")
        return False


def convert_dataset(input_dir, output_dir, dataset_name):
    """
    Convert all JSON files in a dataset directory to CSV format.
    
    Args:
        input_dir (Path): Input dataset directory
        output_dir (Path): Output dataset directory
        dataset_name (str): Name of the dataset
        
    Returns:
        bool: True if all files converted successfully
    """
    logger.info(f"Converting dataset: {dataset_name}")
    
    # Find JSON files in the input directory
    json_files = list(input_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return False
    
    success_count = 0
    for json_file in json_files:
        logger.info(f"Processing: {json_file.name}")
        
        # Load JSON data
        json_data = load_json_data(json_file)
        if not json_data:
            continue
        
        # Extract respondent data
        headers, rows = extract_respondent_data(json_data)
        if not headers or not rows:
            logger.warning(f"No valid data found in {json_file.name}")
            continue
        
        # Generate output filename
        csv_filename = json_file.stem + ".csv"
        output_file = output_dir / csv_filename
        
        # Save CSV file
        if save_csv_file(headers, rows, str(output_file)):
            success_count += 1
        
        logger.info(f"Successfully converted {json_file.name} -> {csv_filename}")
    
    logger.info(f"Dataset {dataset_name}: {success_count}/{len(json_files)} files converted successfully")
    return success_count == len(json_files)


def main():
    """Main function to convert all datasets."""
    
    # Define paths
    input_base_dir = Path("preprocessed_data")
    output_base_dir = Path("preprocessed_data_csv")
    
    logger.info("Starting JSON to CSV conversion for Q_Benchmark preprocessed data")
    logger.info(f"Input directory: {input_base_dir}")
    logger.info(f"Output directory: {output_base_dir}")
    
    # Check if input directory exists
    if not input_base_dir.exists():
        logger.error(f"Input directory does not exist: {input_base_dir}")
        return 1
    
    # Create output directory
    output_base_dir.mkdir(exist_ok=True)
    
    # Find all dataset directories
    dataset_dirs = [d for d in input_base_dir.iterdir() if d.is_dir()]
    if not dataset_dirs:
        logger.error(f"No dataset directories found in {input_base_dir}")
        return 1
    
    logger.info(f"Found {len(dataset_dirs)} datasets to convert")
    
    # Convert each dataset
    success_count = 0
    total_count = len(dataset_dirs)
    
    for dataset_dir in sorted(dataset_dirs):
        dataset_name = dataset_dir.name
        output_dataset_dir = output_base_dir / dataset_name
        
        # Create output dataset directory
        output_dataset_dir.mkdir(exist_ok=True)
        
        # Convert dataset
        if convert_dataset(dataset_dir, output_dataset_dir, dataset_name):
            success_count += 1
    
    # Print summary
    logger.info("="*60)
    logger.info("CONVERSION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total datasets: {total_count}")
    logger.info(f"Successfully converted: {success_count}")
    logger.info(f"Failed: {total_count - success_count}")
    logger.info(f"Output directory: {output_base_dir}")
    logger.info("="*60)
    
    if success_count == total_count:
        logger.info("All datasets converted successfully!")
        return 0
    else:
        logger.error(f"Some conversions failed. Check logs above.")
        return 1


if __name__ == "__main__":
    exit(main())