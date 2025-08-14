#!/usr/bin/env python3
"""
Numeric Ranking Generator for Q_Benchmark Data Obfuscation

This script creates rankings for ONLY numeric attributes in each dataset, 
ranking from smallest to largest. The rankings will be used to implement
rank swapping data obfuscation.

Usage:
    python numeric_ranking_generator.py
"""

import os
import csv
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_numeric_column(values: List[str], column_name: str) -> bool:
    """
    Determine if a column contains numeric values.
    
    Args:
        values: List of string values from the column
        column_name: Name of the column
        
    Returns:
        bool: True if column is numeric, False otherwise
    """
    if column_name.lower() in ['respondent']:
        return True  # Force respondent to be treated as numeric
    
    # Remove empty values for analysis
    non_empty_values = [v.strip() for v in values if v.strip()]
    if not non_empty_values:
        return False
    
    numeric_count = 0
    total_count = len(non_empty_values)
    
    for value in non_empty_values[:100]:  # Sample first 100 values for efficiency
        try:
            # Try to convert to float
            float(value)
            numeric_count += 1
        except (ValueError, TypeError):
            # Check if it's a single character (like 'a', 'b', 'c' for multiple choice)
            if len(value) == 1 and value.isalpha():
                numeric_count += 1  # Treat single letters as ordinal/numeric
            continue
    
    # Consider numeric if >80% of values can be converted or are single letters
    numeric_ratio = numeric_count / min(total_count, 100)
    logger.debug(f"Column '{column_name}': {numeric_ratio:.2%} numeric values")
    
    return numeric_ratio > 0.8


def convert_to_numeric(value: str, column_name: str) -> Optional[float]:
    """
    Convert a string value to numeric for ranking purposes.
    
    Args:
        value: String value to convert
        column_name: Name of the column
        
    Returns:
        float: Numeric value or None if cannot convert
    """
    value = value.strip()
    if not value:
        return None
    
    # Try direct float conversion first
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    
    # Handle single character ordinal values (a, b, c, etc.)
    if len(value) == 1 and value.isalpha():
        return float(ord(value.lower()) - ord('a') + 1)
    
    # Handle specific date formats if needed (basic YYYY-MM-DD)
    if '-' in value and len(value.split('-')) == 3:
        try:
            year, month, day = value.split('-')
            # Convert to days since year 2000 for ranking purposes
            return float(int(year) - 2000) * 365 + float(int(month)) * 30 + float(int(day))
        except (ValueError, TypeError):
            pass
    
    # If all else fails, return None
    return None


def create_numeric_rankings_for_dataset(csv_file_path: Path) -> Dict[str, Any]:
    """
    Create rankings for ONLY numeric attributes in a dataset.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        Dict containing numeric rankings and metadata
    """
    logger.info(f"Processing dataset: {csv_file_path.name}")
    
    try:
        # Read CSV file
        data_rows = []
        headers = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                # Pad row with empty strings if it's shorter than headers
                while len(row) < len(headers):
                    row.append('')
                data_rows.append(row)
        
        dataset_name = csv_file_path.parent.name
        
        logger.info(f"Loaded {len(data_rows)} rows and {len(headers)} columns")
        
        # Initialize results - only for numeric columns
        rankings_data = {
            'dataset_name': dataset_name,
            'total_records': len(data_rows),
            'numeric_columns': {},
            'numeric_column_names': []
        }
        
        # Process each column - identify numeric columns first
        for col_idx, column_name in enumerate(headers):
            # Get column values as strings
            column_values = [row[col_idx] if col_idx < len(row) else '' for row in data_rows]
            
            # Check if column is numeric
            if is_numeric_column(column_values, column_name):
                logger.info(f"Processing numeric column: {column_name}")
                rankings_data['numeric_column_names'].append(column_name)
                
                # Convert to numeric values for ranking
                numeric_values = []
                original_indices = []
                
                for idx, value in enumerate(column_values):
                    numeric_val = convert_to_numeric(value, column_name)
                    if numeric_val is not None:
                        numeric_values.append(numeric_val)
                        original_indices.append(idx)
                
                if numeric_values:
                    # Create rankings - sort indices by their numeric values (smallest to largest)
                    sorted_pairs = sorted(zip(numeric_values, original_indices))
                    
                    # Create rank mapping: original_index -> rank (1-based, smallest=1)
                    rank_mapping = {}
                    for rank, (numeric_val, original_idx) in enumerate(sorted_pairs):
                        rank_mapping[original_idx] = rank + 1  # 1-based ranking
                    
                    # Create full ranking list (empty string for non-numeric values)
                    rankings = []
                    for idx in range(len(column_values)):
                        rank_val = rank_mapping.get(idx, '')
                        rankings.append(str(rank_val) if rank_val != '' else '')
                    
                    rankings_data['numeric_columns'][column_name] = {
                        'rankings': rankings,
                        'valid_numeric_count': len(numeric_values),
                        'min_value': min(numeric_values),
                        'max_value': max(numeric_values),
                        'unique_values': len(set(numeric_values))
                    }
                    
                    logger.info(f"  Created rankings for {len(numeric_values)} numeric values (range: {min(numeric_values):.2f} - {max(numeric_values):.2f})")
                else:
                    logger.warning(f"  No valid numeric values found in column '{column_name}'")
            else:
                logger.info(f"Skipping non-numeric column: {column_name}")
        
        logger.info(f"Dataset summary: {len(rankings_data['numeric_column_names'])} numeric columns identified")
        
        return rankings_data
        
    except Exception as e:
        logger.error(f"Error processing dataset {csv_file_path}: {e}")
        raise


def save_numeric_rankings_to_csv(rankings_data: Dict[str, Any], output_file: Path):
    """
    Save numeric rankings data to CSV file.
    
    Args:
        rankings_data: Rankings data dictionary
        output_file: Path to save the rankings CSV
    """
    try:
        if not rankings_data['numeric_column_names']:
            logger.warning("No numeric columns found - skipping CSV creation")
            return
        
        # Prepare data for CSV output
        rows = []
        
        # Get the number of records
        n_records = rankings_data['total_records']
        
        # Create header row - only numeric columns
        headers = rankings_data['numeric_column_names']
        
        # Create data rows
        for record_idx in range(n_records):
            row = []
            
            # Add rankings for each numeric column only
            for column_name in headers:
                if column_name in rankings_data['numeric_columns']:
                    column_info = rankings_data['numeric_columns'][column_name]
                    ranking = column_info['rankings'][record_idx] if record_idx < len(column_info['rankings']) else ''
                    row.append(ranking)
                else:
                    row.append('')  # Shouldn't happen, but safety check
            
            rows.append(row)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Saved numeric rankings to: {output_file}")
        logger.info(f"Rankings shape: {len(rows)} rows x {len(headers)} columns")
        
        # Log summary statistics
        for col_name in headers:
            if col_name in rankings_data['numeric_columns']:
                col_info = rankings_data['numeric_columns'][col_name]
                logger.info(f"  {col_name}: {col_info['valid_numeric_count']} values, "
                           f"range {col_info['min_value']:.2f}-{col_info['max_value']:.2f}")
        
    except Exception as e:
        logger.error(f"Error saving rankings to {output_file}: {e}")
        raise


def process_all_datasets(input_base_dir: str = "preprocessed_data_csv"):
    """
    Process all datasets to create numeric rankings and save them back to preprocessed_data_csv.
    
    Args:
        input_base_dir: Directory containing CSV datasets
    """
    input_path = Path(input_base_dir)
    
    logger.info(f"Processing all datasets from: {input_path}")
    logger.info(f"Saving rankings back to: {input_path}")
    
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        return False
    
    # Find all CSV files in dataset subdirectories
    csv_files = list(input_path.glob("**/*.csv"))
    # Filter out existing ranking files
    csv_files = [f for f in csv_files if not f.name.endswith('.rankings.csv')]
    
    if not csv_files:
        logger.error(f"No CSV files found in {input_path}")
        return False
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    success_count = 0
    
    for csv_file in sorted(csv_files):
        try:
            # Create numeric rankings for this dataset
            rankings_data = create_numeric_rankings_for_dataset(csv_file)
            
            # Skip if no numeric columns found
            if not rankings_data['numeric_column_names']:
                logger.warning(f"No numeric columns found in {csv_file.name} - skipping")
                continue
            
            # Determine output file path (same directory as input)
            output_file = csv_file.with_suffix('.rankings.csv')
            
            # Save rankings
            save_numeric_rankings_to_csv(rankings_data, output_file)
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Failed to process {csv_file}: {e}")
            continue
    
    # Print summary
    logger.info("="*60)
    logger.info("NUMERIC RANKING GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total CSV files: {len(csv_files)}")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed: {len(csv_files) - success_count}")
    logger.info(f"Rankings saved to: {input_path}")
    logger.info("="*60)
    
    return success_count == len(csv_files)


def main():
    """Main function to run the numeric ranking generation."""
    logger.info("Starting numeric ranking generation for Q_Benchmark datasets")
    
    success = process_all_datasets()
    
    if success:
        logger.info("All datasets processed successfully!")
        return 0
    else:
        logger.error("Some datasets failed to process. Check logs above.")
        return 1


if __name__ == "__main__":
    exit(main())