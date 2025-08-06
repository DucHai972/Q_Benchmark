#!/usr/bin/env python3
"""
Script to fix XML and HTML formats in answer_reverse_lookup to exactly match answer_lookup structure
"""

import os
import json
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

def load_json_data(json_file):
    """Load JSON data from file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_xml_from_json(data):
    """Generate XML content matching answer_lookup format exactly"""
    root = Element('questionnaire')
    
    # Questions section
    questions_elem = SubElement(root, 'questions')
    
    for key, value in data['questions'].items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group
            group_elem = SubElement(questions_elem, 'question_group')
            group_elem.set('id', key)
            
            base_elem = SubElement(group_elem, 'base_question')
            base_elem.text = value['base_question']
            
            sub_questions_elem = SubElement(group_elem, 'sub_questions')
            for sub_key, sub_value in value['sub_questions'].items():
                sub_elem = SubElement(sub_questions_elem, 'question')
                sub_elem.set('id', sub_key)
                sub_elem.text = sub_value
        else:
            # Regular question
            question_elem = SubElement(questions_elem, 'question')
            question_elem.set('id', key)
            question_elem.text = value
    
    # Responses section
    responses_elem = SubElement(root, 'responses')
    
    for response in data['responses']:
        respondent_elem = SubElement(responses_elem, 'respondent')
        respondent_elem.set('id', str(response['respondent']))
        
        for key, value in response['answers'].items():
            if isinstance(value, dict):
                # Grouped response using answer_group with question attribute
                group_elem = SubElement(respondent_elem, 'answer_group')
                group_elem.set('question', key)
                
                for sub_key, sub_value in value.items():
                    answer_elem = SubElement(group_elem, 'answer')
                    answer_elem.set('sub_question', sub_key)
                    answer_elem.text = str(sub_value)
            else:
                # Individual response using answer with question attribute
                answer_elem = SubElement(respondent_elem, 'answer')
                answer_elem.set('question', key)
                answer_elem.text = str(value)
    
    # Convert to pretty XML string
    xml_str = tostring(root, encoding='unicode')
    dom = xml.dom.minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')[23:]  # Remove XML declaration

def generate_html_from_json(data):
    """Generate HTML content matching answer_lookup format exactly"""
    html_content = """<!DOCTYPE html>
<html>
<head>
<title>Survey Data</title>
</head>
<body>
<h1>Questions</h1>
<ul>"""
    
    questions = data['questions']
    
    for key, value in questions.items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group
            html_content += f'''
  <li>
    <strong>{key}:</strong> {value["base_question"]}
    <ul>'''
            for sub_key, sub_value in value['sub_questions'].items():
                html_content += f'\n      <li><strong>{sub_key}:</strong> {sub_value}</li>'
            html_content += '\n    </ul>\n  </li>'
        else:
            # Regular question
            html_content += f'\n  <li><strong>{key}:</strong> {value}</li>'
    
    html_content += '\n</ul>\n<h1>Responses</h1>\n'
    
    # Add responses in answer_lookup format
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        html_content += f'\n<h2>Respondent {respondent_id}</h2>\n<ul>'
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # Grouped response
                html_content += f'\n  <li>\n    <strong>{key}:</strong>\n    <ul>'
                for sub_key, sub_value in value.items():
                    html_content += f'\n      <li><strong>{sub_key}:</strong> {sub_value}</li>'
                html_content += '\n    </ul>\n  </li>'
            else:
                # Individual response
                html_content += f'\n  <li><strong>{key}:</strong> {value}</li>'
        
        html_content += '\n</ul>'
    
    html_content += '\n</body>\n</html>'
    return html_content

def process_all_cases():
    """Process all case files in answer_reverse_lookup"""
    base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_reverse_lookup'
    
    # Get all JSON files
    json_path = os.path.join(base_path, 'json')
    json_files = [f for f in os.listdir(json_path) if f.endswith('.json')]
    
    print(f"Fixing XML and HTML formats for {len(json_files)} case files...")
    
    for json_file in sorted(json_files):
        case_name = json_file.replace('.json', '')
        print(f"Processing {case_name}...")
        
        # Load JSON data
        json_filepath = os.path.join(json_path, json_file)
        data = load_json_data(json_filepath)
        
        # Generate and write corrected XML format
        xml_content = generate_xml_from_json(data)
        xml_filepath = os.path.join(base_path, 'xml', f'{case_name}.xml')
        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Generate and write corrected HTML format
        html_content = generate_html_from_json(data)
        html_filepath = os.path.join(base_path, 'html', f'{case_name}.html')
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    print(f"Successfully fixed XML and HTML formats for all {len(json_files)} cases!")
    print("XML and HTML formats now exactly match answer_lookup structure.")

if __name__ == "__main__":
    process_all_cases()