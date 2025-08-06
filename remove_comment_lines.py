#!/usr/bin/env python3
import re
from pathlib import Path


def remove_question_group_comments(file_path):
    """Remove question group comment lines from TTL file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    filtered_lines = []
    
    # Comment patterns to remove
    comment_patterns = [
        "# Parental Education Question Group",
        "# Emotional Regulation Frequency Question Group", 
        "# Anxiety Symptoms Frequency Question Group",
        "# Depressive Symptoms Frequency Question Group"
    ]
    
    for line in lines:
        # Check if line matches any of the comment patterns
        if line.strip() in comment_patterns:
            continue  # Skip this line
        filtered_lines.append(line)
    
    # Write back the filtered content
    with open(file_path, 'w') as f:
        f.write('\n'.join(filtered_lines))


def main():
    ttl_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_lookup/ttl")
    
    # Get all TTL files
    ttl_files = list(ttl_dir.glob("case_*.ttl"))
    
    print(f"Found {len(ttl_files)} TTL files to process")
    
    for ttl_file in ttl_files:
        print(f"Removing comment lines from {ttl_file.name}...")
        try:
            remove_question_group_comments(ttl_file)
            print(f"✓ Successfully processed {ttl_file.name}")
        except Exception as e:
            print(f"✗ Error processing {ttl_file.name}: {e}")
    
    print("Comment removal complete!")


if __name__ == "__main__":
    main()