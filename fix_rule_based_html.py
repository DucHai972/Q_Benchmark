#!/usr/bin/env python3
import json
import os
from pathlib import Path


def generate_html_from_json(json_data):
    """Generate HTML content from JSON data matching answer_lookup format"""
    
    html_lines = []
    
    # HTML header
    html_lines.extend([
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>Survey Data</title>",
        "</head>",
        "<body>",
        "<h1>Questions</h1>",
        "<ul>"
    ])
    
    # Generate questions section
    questions = json_data.get("questions", {})
    
    for key, value in questions.items():
        if isinstance(value, dict) and "base_question" in value:
            # Grouped question with sub-questions
            html_lines.append(f"  <li>")
            html_lines.append(f"    <strong>{key}:</strong> {value['base_question']}")
            html_lines.append("    <ul>")
            
            for sub_key, sub_value in value.get("sub_questions", {}).items():
                html_lines.append(f"      <li><strong>{sub_key}:</strong> {sub_value}</li>")
            
            html_lines.append("    </ul>")
            html_lines.append("  </li>")
        else:
            # Simple question
            html_lines.append(f"  <li><strong>{key}:</strong> {value}</li>")
    
    html_lines.append("</ul>")
    
    # Generate responses section
    html_lines.append("<h1>Responses</h1>")
    
    responses = json_data.get("responses", [])
    
    for response in responses:
        respondent_id = response.get("respondent", "Unknown")
        html_lines.append(f"<h2>Respondent {respondent_id}</h2>")
        html_lines.append("<ul>")
        
        answers = response.get("answers", {})
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # Grouped response
                html_lines.append(f"  <li>")
                html_lines.append(f"    <strong>{key}:</strong>")
                html_lines.append("    <ul>")
                
                for sub_key, sub_value in value.items():
                    html_lines.append(f"      <li><strong>{sub_key}:</strong> {sub_value}</li>")
                
                html_lines.append("    </ul>")
                html_lines.append("  </li>")
            else:
                # Simple response
                html_lines.append(f"  <li><strong>{key}:</strong> {value}</li>")
        
        html_lines.append("</ul>")
    
    # HTML footer
    html_lines.extend([
        "</body>",
        "</html>"
    ])
    
    return '\n'.join(html_lines)


def fix_html_file(json_file_path, html_file_path):
    """Fix HTML file using corresponding JSON data"""
    
    # Read JSON data
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    
    # Generate HTML content
    html_content = generate_html_from_json(json_data)
    
    # Write HTML file
    with open(html_file_path, 'w') as f:
        f.write(html_content)


def main():
    base_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/rule_based_querying")
    json_dir = base_dir / "json"
    html_dir = base_dir / "html"
    
    # Get all JSON files
    json_files = list(json_dir.glob("case_*.json"))
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        # Find corresponding HTML file
        html_file = html_dir / f"{json_file.stem}.html"
        
        print(f"Fixing {html_file.name} using {json_file.name}...")
        try:
            fix_html_file(json_file, html_file)
            print(f"✓ Successfully fixed {html_file.name}")
        except Exception as e:
            print(f"✗ Error fixing {html_file.name}: {e}")
    
    print("HTML fixing complete!")


if __name__ == "__main__":
    main()