#!/usr/bin/env python3
"""
Data Ranking Generator for Q_Benchmark Data Obfuscation

This script creates rankings for all attributes in each dataset to prepare 
for rank swapping data obfuscation. The rankings will be used to implement
rank swapping where values are swapped within a window around their rank position.

Usage:
    python data_ranking_generator.py
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


def create_rankings_for_dataset(csv_file_path: Path) -> Dict[str, Any]:
    """
    Create rankings for all attributes in a dataset.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        Dict containing rankings and metadata
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
        
        # Initialize results
        rankings_data = {
            'dataset_name': dataset_name,
            'total_records': len(data_rows),
            'columns': {},
            'numeric_columns': [],
            'non_numeric_columns': []
        }
        
        # Process each column
        for col_idx, column_name in enumerate(headers):
            logger.info(f"Processing column: {column_name}")
            
            # Get column values as strings
            column_values = [row[col_idx] if col_idx < len(row) else '' for row in data_rows]
            
            # Determine if column is numeric
            is_numeric = is_numeric_column(column_values, column_name)
            
            column_info = {
                'name': column_name,
                'is_numeric': is_numeric,
                'total_values': len(column_values),
                'empty_values': sum(1 for v in column_values if not v.strip()),
            }
            
            if is_numeric:
                rankings_data['numeric_columns'].append(column_name)
                
                # Convert to numeric values for ranking
                numeric_values = []
                original_indices = []
                
                for idx, value in enumerate(column_values):
                    numeric_val = convert_to_numeric(value, column_name)
                    if numeric_val is not None:
                        numeric_values.append(numeric_val)
                        original_indices.append(idx)
                
                if numeric_values:
                    # Create rankings - sort indices by their numeric values
                    sorted_pairs = sorted(zip(numeric_values, original_indices))
                    
                    # Create rank mapping: original_index -> rank
                    rank_mapping = {}
                    for rank, (numeric_val, original_idx) in enumerate(sorted_pairs):
                        rank_mapping[original_idx] = rank + 1  # 1-based ranking
                    
                    # Create full ranking list (None for non-numeric values)
                    rankings = []
                    for idx in range(len(column_values)):
                        rankings.append(rank_mapping.get(idx, None))
                    
                    column_info.update({
                        'rankings': rankings,
                        'valid_numeric_count': len(numeric_values),
                        'min_value': min(numeric_values),
                        'max_value': max(numeric_values),
                        'unique_values': len(set(numeric_values))
                    })
                    
                    logger.info(f"  Created rankings for {len(numeric_values)} numeric values")
                else:
                    column_info['rankings'] = [None] * len(column_values)
                    logger.warning(f"  No valid numeric values found in column '{column_name}'")
            else:
                rankings_data['non_numeric_columns'].append(column_name)
                
                # For non-numeric columns, create rankings based on string sorting
                value_index_pairs = [(v, idx) for idx, v in enumerate(column_values) if v.strip()]
                sorted_pairs = sorted(value_index_pairs)
                
                rank_mapping = {}
                for rank, (value, original_idx) in enumerate(sorted_pairs):
                    rank_mapping[original_idx] = rank + 1
                
                rankings = []
                for idx in range(len(column_values)):
                    rankings.append(rank_mapping.get(idx, None))
                
                column_info.update({
                    'rankings': rankings,
                    'valid_string_count': len(value_index_pairs),
                    'unique_values': len(set(v for v, _ in value_index_pairs))
                })
                
                logger.info(f"  Created string-based rankings for {len(value_index_pairs)} values")
            
            rankings_data['columns'][column_name] = column_info
        
        logger.info(f"Dataset summary: {len(rankings_data['numeric_columns'])} numeric, "
                   f"{len(rankings_data['non_numeric_columns'])} non-numeric columns")
        
        return rankings_data
        
    except Exception as e:
        logger.error(f"Error processing dataset {csv_file_path}: {e}")
        raise


def save_rankings_to_csv(rankings_data: Dict[str, Any], output_file: Path):
    """
    Save rankings data to CSV file for later use in rank swapping.
    
    Args:
        rankings_data: Rankings data dictionary
        output_file: Path to save the rankings CSV
    """
    try:
        # Prepare data for CSV output
        rows = []
        
        # Get the number of records
        n_records = rankings_data['total_records']
        
        # Create header row
        headers = ['record_index'] + list(rankings_data['columns'].keys()) + ['_metadata']
        
        # Create data rows
        for record_idx in range(n_records):
            row = [record_idx]  # Start with record index
            
            # Add rankings for each column
            for column_name in rankings_data['columns'].keys():
                column_info = rankings_data['columns'][column_name]
                ranking = column_info['rankings'][record_idx] if record_idx < len(column_info['rankings']) else None
                row.append(ranking)
            
            # Add metadata for first row only
            if record_idx == 0:
                metadata = {
                    'dataset': rankings_data['dataset_name'],
                    'total_records': rankings_data['total_records'],
                    'numeric_columns': rankings_data['numeric_columns'],
                    'non_numeric_columns': rankings_data['non_numeric_columns']
                }
                row.append(str(metadata))
            else:
                row.append('')
            
            rows.append(row)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Saved rankings to: {output_file}")
        logger.info(f"Rankings shape: {len(rows)} rows x {len(headers)} columns")
        
    except Exception as e:
        logger.error(f"Error saving rankings to {output_file}: {e}")
        raise


def process_all_datasets(input_base_dir: str = "preprocessed_data_csv", 
                        output_base_dir: str = "data_rankings"):
    """
    Process all datasets to create rankings.
    
    Args:
        input_base_dir: Directory containing CSV datasets
        output_base_dir: Directory to save ranking files
    """
    input_path = Path(input_base_dir)
    output_path = Path(output_base_dir)
    
    logger.info(f"Processing all datasets from: {input_path}")
    logger.info(f"Saving rankings to: {output_path}")
    
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        return False
    
    # Find all CSV files in dataset subdirectories
    csv_files = list(input_path.glob("**/*.csv"))
    if not csv_files:
        logger.error(f"No CSV files found in {input_path}")
        return False
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    success_count = 0
    
    for csv_file in sorted(csv_files):
        try:
            # Create rankings for this dataset
            rankings_data = create_rankings_for_dataset(csv_file)
            
            # Determine output file path
            relative_path = csv_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.rankings.csv')
            
            # Save rankings
            save_rankings_to_csv(rankings_data, output_file)
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Failed to process {csv_file}: {e}")
            continue
    
    # Print summary
    logger.info("="*60)
    logger.info("RANKING GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total CSV files: {len(csv_files)}")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed: {len(csv_files) - success_count}")
    logger.info(f"Rankings saved to: {output_path}")
    logger.info("="*60)
    
    return success_count == len(csv_files)


def main():
    """Main function to run the ranking generation."""
    logger.info("Starting data ranking generation for Q_Benchmark datasets")
    
    success = process_all_datasets()
    
    if success:
        logger.info("All datasets processed successfully!")
        return 0
    else:
        logger.error("Some datasets failed to process. Check logs above.")
        return 1


if __name__ == "__main__":
    exit(main())