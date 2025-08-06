#!/usr/bin/env python3
"""
Script to fix respondent IDs in healthcare-dataset conceptual_aggregation HTML files
to match the actual respondent IDs from JSON files
"""

import os
import json

def load_json_data(json_file):
    """Load JSON data from file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html_from_json(data):
    """Generate HTML content with correct respondent IDs from JSON"""
    html_content = """<!DOCTYPE html>
<html>
<head>
<title>Survey Data</title>
</head>
<body>
<h1>Questions</h1>
<ul>"""
    
    # Add questions
    for key, value in data['questions'].items():
        html_content += f'\n  <li><strong>{key}:</strong> {value}</li>'
    
    html_content += '\n</ul>\n<h1>Responses</h1>'
    
    # Add responses with correct respondent IDs from JSON
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        html_content += f'\n<h2>Respondent {respondent_id}</h2>\n<ul>'
        
        for key, value in answers.items():
            # Convert value to lowercase to match existing format
            if isinstance(value, str) and len(value) == 1 and value.isalpha():
                value = value.lower()
            html_content += f'\n  <li><strong>{key}:</strong> {value}</li>'
        
        html_content += '\n</ul>'
    
    html_content += '\n</body>\n</html>'
    return html_content

def process_all_cases():
    """Process all case files in healthcare-dataset conceptual_aggregation"""
    base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/conceptual_aggregation'
    
    # Get all JSON files
    json_path = os.path.join(base_path, 'json')
    json_files = [f for f in os.listdir(json_path) if f.endswith('.json')]
    
    print(f"Fixing respondent IDs in conceptual_aggregation HTML files for {len(json_files)} case files...")
    
    for json_file in sorted(json_files):
        case_name = json_file.replace('.json', '')
        print(f"Processing {case_name}...")
        
        # Load JSON data
        json_filepath = os.path.join(json_path, json_file)
        data = load_json_data(json_filepath)
        
        # Generate corrected HTML with proper respondent IDs
        html_content = generate_html_from_json(data)
        html_filepath = os.path.join(base_path, 'html', f'{case_name}.html')
        
        # Write the corrected HTML file
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Show the actual respondent IDs being used
        respondent_ids = [resp['respondent'] for resp in data['responses']]
        print(f"  - Updated respondent IDs: {respondent_ids}")
    
    print(f"Successfully fixed respondent IDs in conceptual_aggregation HTML files for all {len(json_files)} cases!")
    print("HTML respondent IDs now match the JSON data exactly.")

if __name__ == "__main__":
    process_all_cases()