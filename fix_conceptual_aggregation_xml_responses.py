#!/usr/bin/env python3
"""
Script to fix XML format in conceptual_aggregation by adding missing responses
from JSON format data
"""

import os
import json
import xml.dom.minidom as minidom
from xml.dom.minidom import Document

def create_response_xml(respondent_data):
    """Create XML elements for a single respondent's responses"""
    respondent_id = respondent_data['respondent']
    answers = respondent_data['answers']
    
    # Create respondent element
    respondent_elem = f'    <respondent id="{respondent_id}">\n'
    
    # Add individual answers
    for question_key, answer_value in answers.items():
        if isinstance(answer_value, dict):
            # Handle grouped questions (Parental Education, Emotional Regulation, etc.)
            respondent_elem += f'      <answer_group question="{question_key}">\n'
            for sub_key, sub_value in answer_value.items():
                respondent_elem += f'        <answer sub_question="{sub_key}">{sub_value}</answer>\n'
            respondent_elem += f'      </answer_group>\n'
        else:
            # Handle simple questions
            respondent_elem += f'      <answer question="{question_key}">{answer_value}</answer>\n'
    
    respondent_elem += '    </respondent>\n'
    return respondent_elem

def fix_xml_responses(json_file_path, xml_file_path):
    """Fix XML file by adding responses from JSON data"""
    
    # Read JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Read current XML content
    with open(xml_file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Check if responses are already populated
    if '<respondent id=' in xml_content:
        return False  # No changes needed
    
    # Generate response XML from JSON data
    responses_xml = ""
    for respondent_data in json_data['responses']:
        responses_xml += create_response_xml(respondent_data)
    
    # Replace empty responses section with populated one
    empty_responses = '  <responses>\n  </responses>'
    populated_responses = f'  <responses>\n{responses_xml}  </responses>'
    
    if empty_responses in xml_content:
        fixed_content = xml_content.replace(empty_responses, populated_responses)
        
        # Write the fixed content back
        with open(xml_file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return True
    else:
        print(f"Warning: Expected empty responses section not found in {xml_file_path}")
        return False

def process_all_conceptual_aggregation_xml_files():
    """Process all XML files in conceptual_aggregation to add missing responses"""
    json_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/conceptual_aggregation/json'
    xml_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/conceptual_aggregation/xml'
    
    if not os.path.exists(json_base_path):
        print(f"Error: JSON directory not found: {json_base_path}")
        return
    
    if not os.path.exists(xml_base_path):
        print(f"Error: XML directory not found: {xml_base_path}")
        return
    
    # Get all JSON files to use as source
    json_files = [f for f in os.listdir(json_base_path) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    processed_count = 0
    changes_made = 0
    
    for json_file in sorted(json_files):
        # Determine corresponding XML file
        xml_file = json_file.replace('.json', '.xml')
        json_file_path = os.path.join(json_base_path, json_file)
        xml_file_path = os.path.join(xml_base_path, xml_file)
        
        if not os.path.exists(xml_file_path):
            print(f"Warning: XML file not found: {xml_file}")
            continue
        
        # Fix the XML file using JSON data
        try:
            if fix_xml_responses(json_file_path, xml_file_path):
                changes_made += 1
                print(f"Processing {xml_file}: Added response data from JSON")
            else:
                print(f"Processing {xml_file}: No changes needed (responses already exist)")
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")
        
        processed_count += 1
    
    print(f"\nProcessing complete!")
    print(f"- Total files processed: {processed_count}")
    print(f"- Files with changes: {changes_made}")
    print(f"- Files without changes: {processed_count - changes_made}")
    
    if changes_made > 0:
        print(f"\nSuccessfully added response data to conceptual_aggregation XML files!")
        print(f"- All responses now include respondent data with individual and grouped answers")
        print(f"- XML format now consistent with JSON data structure")
    else:
        print(f"\nAll XML files already had complete response data.")

if __name__ == "__main__":
    process_all_conceptual_aggregation_xml_files()