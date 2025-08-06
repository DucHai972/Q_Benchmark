#!/usr/bin/env python3
"""
Script to standardize answer_reverse_lookup formats to match answer_lookup hierarchical structure
"""

import os
import json
import ast
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

def load_json_data(json_file):
    """Load JSON data from file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_ttl_from_json(data):
    """Generate TTL content from JSON data using answer_lookup hierarchical format"""
    ttl_content = """@prefix : <http://example.org/survey#> .
@prefix pred: <http://example.org/predicate#> .
@prefix qg: <http://example.org/question_group#> .

# Questions"""
    
    questions = data['questions']
    
    # Individual questions first
    for key, value in questions.items():
        if isinstance(value, dict) and 'base_question' in value:
            # This is a question group - create base question and sub-questions
            ttl_content += f'\n:QG{key.replace(" ", "_")} pred:BaseQuestion "{value["base_question"]}" ;\n'
            sub_questions = []
            for sub_key, sub_value in value['sub_questions'].items():
                sub_question_id = f':Q{key.replace(" ", "_")}_{sub_key.replace(" ", "_")}'
                sub_questions.append(sub_question_id)
                ttl_content += f'    qg:hasSubQuestion {sub_question_id}{"," if sub_key != list(value["sub_questions"].keys())[-1] else " ."}'
                if sub_key == list(value["sub_questions"].keys())[-1]:
                    ttl_content += '\n'
            
            # Add sub-question definitions
            for sub_key, sub_value in value['sub_questions'].items():
                sub_question_id = f':Q{key.replace(" ", "_")}_{sub_key.replace(" ", "_")}'
                ttl_content += f'{sub_question_id} pred:Text "{sub_value}" .\n'
        else:
            # Regular question
            ttl_content += f'\n:Q{key.replace(" ", "_")} pred:Text "{value}" .'
    
    ttl_content += '\n\n# Responses'
    
    # Add responses using hierarchical format
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        ttl_content += f'\n:R{respondent_id}'
        
        # Individual responses first
        individual_responses = []
        group_responses = []
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # This is a grouped response
                group_responses.append((key, value))
            else:
                # Individual response
                individual_responses.append(f'     pred:{key.replace(" ", "_")} {value}')
        
        if individual_responses:
            ttl_content += ' ' + ' ;\n'.join(individual_responses) + ' .\n'
        
        # Add grouped responses
        for group_key, group_values in group_responses:
            group_id = f':R{respondent_id}_{group_key.replace(" ", "_")}'
            ttl_content += f'\n{group_id}'
            
            group_items = []
            for sub_key, sub_value in group_values.items():
                group_items.append(f'                       pred:{sub_key.replace(" ", "_")} {sub_value}')
            
            ttl_content += '\n' + ' ;\n'.join(group_items) + ' .\n'
            ttl_content += f':R{respondent_id} pred:hasGroupResponse {group_id} .\n'
    
    return ttl_content

def generate_txt_from_json(data):
    """Generate TXT content from JSON data using answer_lookup hierarchical format"""
    txt_content = """Survey Data
==================================================

Questions:"""
    
    questions = data['questions']
    question_num = 1
    
    for key, value in questions.items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group with sub-questions
            txt_content += f'\n{question_num}. {key}: {value["base_question"]}'
            for sub_key, sub_value in value['sub_questions'].items():
                txt_content += f'\n   - {sub_key}: {sub_value}'
        else:
            # Regular question
            txt_content += f'\n{question_num}. {key}: {value}'
        question_num += 1
    
    txt_content += '\n\nResponses:\n==================================================\n'
    
    # Add responses in hierarchical format
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        txt_content += f'\nRespondent {respondent_id}:\n------------------------------'
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # Grouped response
                txt_content += f'\n{key}:'
                for sub_key, sub_value in value.items():
                    txt_content += f'\n  - {sub_key}: {sub_value}'
            else:
                # Individual response
                txt_content += f'\n{key}: {value}'
        
        txt_content += '\n'
    
    return txt_content

def generate_xml_from_json(data):
    """Generate XML content from JSON data using answer_lookup hierarchical format"""
    root = Element('survey_data')
    
    # Questions section
    questions_elem = SubElement(root, 'questions')
    
    for key, value in data['questions'].items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group
            group_elem = SubElement(questions_elem, 'question_group')
            group_elem.set('name', key)
            
            base_elem = SubElement(group_elem, 'base_question')
            base_elem.text = value['base_question']
            
            sub_questions_elem = SubElement(group_elem, 'sub_questions')
            for sub_key, sub_value in value['sub_questions'].items():
                sub_elem = SubElement(sub_questions_elem, 'question')
                sub_elem.set('name', sub_key)
                sub_elem.text = sub_value
        else:
            # Regular question
            question_elem = SubElement(questions_elem, 'question')
            question_elem.set('name', key)
            question_elem.text = value
    
    # Responses section
    responses_elem = SubElement(root, 'responses')
    
    for response in data['responses']:
        respondent_elem = SubElement(responses_elem, 'respondent')
        respondent_elem.set('id', str(response['respondent']))
        
        for key, value in response['answers'].items():
            if isinstance(value, dict):
                # Grouped response
                group_elem = SubElement(respondent_elem, 'response_group')
                group_elem.set('name', key)
                
                for sub_key, sub_value in value.items():
                    response_elem = SubElement(group_elem, 'response')
                    response_elem.set('name', sub_key)
                    response_elem.text = str(sub_value)
            else:
                # Individual response
                response_elem = SubElement(respondent_elem, 'response')
                response_elem.set('name', key)
                response_elem.text = str(value)
    
    # Convert to pretty XML string
    xml_str = tostring(root, encoding='unicode')
    dom = xml.dom.minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')[23:]  # Remove XML declaration

def generate_md_from_json(data):
    """Generate Markdown content from JSON data using answer_lookup hierarchical format"""
    md_content = """# Survey Data

## Questions

"""
    
    questions = data['questions']
    
    for key, value in questions.items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group
            md_content += f'- **{key}:** {value["base_question"]}\n'
            for sub_key, sub_value in value['sub_questions'].items():
                md_content += f'  - **{sub_key}:** {sub_value}\n'
        else:
            # Regular question
            md_content += f'- **{key}:** {value}\n'
    
    md_content += '\n## Responses\n\n'
    
    # Add responses in hierarchical format
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        md_content += f'### Respondent {respondent_id}\n\n'
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # Grouped response
                md_content += f'- **{key}:**\n'
                for sub_key, sub_value in value.items():
                    md_content += f'  - **{sub_key}:** {sub_value}\n'
            else:
                # Individual response
                md_content += f'- **{key}:** {value}\n'
        
        md_content += '\n'
    
    return md_content

def generate_html_from_json(data):
    """Generate HTML content from JSON data using answer_lookup hierarchical format"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Survey Data</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        ul { margin: 10px 0; }
        li { margin: 5px 0; }
        .respondent { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .question-group { margin: 15px 0; }
        .sub-questions { margin-left: 20px; }
        .response-group { margin: 10px 0; padding: 10px; background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Survey Data</h1>
    
    <h2>Questions</h2>
    <ul>"""
    
    questions = data['questions']
    
    for key, value in questions.items():
        if isinstance(value, dict) and 'base_question' in value:
            # Question group
            html_content += f'''
        <li class="question-group">
            <strong>{key}:</strong> {value["base_question"]}
            <ul class="sub-questions">'''
            for sub_key, sub_value in value['sub_questions'].items():
                html_content += f'\n                <li><strong>{sub_key}:</strong> {sub_value}</li>'
            html_content += '\n            </ul>\n        </li>'
        else:
            # Regular question
            html_content += f'\n        <li><strong>{key}:</strong> {value}</li>'
    
    html_content += '\n    </ul>\n    \n    <h2>Responses</h2>\n'
    
    # Add responses in hierarchical format
    for response in data['responses']:
        respondent_id = response['respondent']
        answers = response['answers']
        
        html_content += f'\n    <div class="respondent">\n        <h3>Respondent {respondent_id}</h3>\n        <ul>'
        
        for key, value in answers.items():
            if isinstance(value, dict):
                # Grouped response
                html_content += f'\n            <li class="response-group">\n                <strong>{key}:</strong>\n                <ul>'
                for sub_key, sub_value in value.items():
                    html_content += f'\n                    <li><strong>{sub_key}:</strong> {sub_value}</li>'
                html_content += '\n                </ul>\n            </li>'
            else:
                # Individual response
                html_content += f'\n            <li><strong>{key}:</strong> {value}</li>'
        
        html_content += '\n        </ul>\n    </div>'
    
    html_content += '\n</body>\n</html>'
    return html_content

def process_all_cases():
    """Process all case files in answer_reverse_lookup"""
    base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_reverse_lookup'
    
    # Get all JSON files
    json_path = os.path.join(base_path, 'json')
    json_files = [f for f in os.listdir(json_path) if f.endswith('.json')]
    
    print(f"Processing {len(json_files)} case files...")
    
    for json_file in sorted(json_files):
        case_name = json_file.replace('.json', '')
        print(f"Processing {case_name}...")
        
        # Load JSON data
        json_filepath = os.path.join(json_path, json_file)
        data = load_json_data(json_filepath)
        
        # Generate and write TTL format
        ttl_content = generate_ttl_from_json(data)
        ttl_filepath = os.path.join(base_path, 'ttl', f'{case_name}.ttl')
        with open(ttl_filepath, 'w', encoding='utf-8') as f:
            f.write(ttl_content)
        
        # Generate and write TXT format
        txt_content = generate_txt_from_json(data)
        txt_filepath = os.path.join(base_path, 'txt', f'{case_name}.txt')
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        # Generate and write XML format
        xml_content = generate_xml_from_json(data)
        xml_filepath = os.path.join(base_path, 'xml', f'{case_name}.xml')
        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Generate and write MD format
        md_content = generate_md_from_json(data)
        md_filepath = os.path.join(base_path, 'md', f'{case_name}.md')
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Generate and write HTML format
        html_content = generate_html_from_json(data)
        html_filepath = os.path.join(base_path, 'html', f'{case_name}.html')
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    print(f"Successfully processed all {len(json_files)} cases!")
    print("All formats (TTL, TXT, XML, MD, HTML) have been standardized to match answer_lookup hierarchical structure.")

if __name__ == "__main__":
    process_all_cases()