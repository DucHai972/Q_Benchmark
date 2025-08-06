#!/usr/bin/env python3
"""
Batch fix nested questions for self-reported-mental-health dataset
Based on the working case_1_modified templates
"""

import json
import os
import re
from pathlib import Path

def copy_template_structure(source_file, target_file, source_respondents, target_respondents):
    """Copy template structure while preserving target respondent data"""
    
    # Read the source template
    with open(source_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Read the target file to get current respondent data
    with open(target_file, 'r', encoding='utf-8') as f:
        target_content = f.read()
    
    format_ext = source_file.suffix.lower()
    
    if format_ext == '.html':
        return fix_html_file(template_content, target_content, source_respondents, target_respondents)
    elif format_ext == '.xml':
        return fix_xml_file(template_content, target_content, source_respondents, target_respondents)
    elif format_ext == '.md':
        return fix_md_file(template_content, target_content, source_respondents, target_respondents)
    elif format_ext == '.txt':
        return fix_txt_file(template_content, target_content, source_respondents, target_respondents)
    elif format_ext == '.ttl':
        return fix_ttl_file(template_content, target_content, source_respondents, target_respondents)
    
    return None

def fix_html_file(template_content, target_content, source_respondents, target_respondents):
    """Fix HTML file using template structure"""
    
    # Extract target respondent data
    target_response_matches = re.findall(
        r'<h2>Respondent (\d+)</h2>\s*<ul>(.*?)</ul>', 
        target_content, 
        re.DOTALL
    )
    
    target_responses = {}
    for resp_id, resp_content in target_response_matches:
        target_responses[resp_id] = resp_content.strip()
    
    # Use template structure but replace responses
    result = template_content
    
    # Replace template respondent data with target respondent data
    for target_id, target_resp in target_responses.items():
        if target_id in source_respondents:
            source_id = source_respondents[target_id]  # Map target to source ID
            # Replace the entire response section for this respondent
            pattern = rf'(<h2>Respondent {re.escape(source_id)}</h2>\s*<ul>).*?(</ul>)'
            replacement = rf'\1\n{target_resp}\n\2'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    
    # Update respondent IDs in headers
    for target_id, source_id in zip(target_responses.keys(), source_respondents.keys()):
        result = result.replace(f'<h2>Respondent {source_id}</h2>', f'<h2>Respondent {target_id}</h2>')
    
    return result

def fix_xml_file(template_content, target_content, source_respondents, target_respondents):
    """Fix XML file using template structure"""
    
    # Extract target respondent data
    target_response_matches = re.findall(
        r'<respondent id="(\d+)">(.*?)</respondent>', 
        target_content, 
        re.DOTALL
    )
    
    target_responses = {}
    for resp_id, resp_content in target_response_matches:
        target_responses[resp_id] = resp_content.strip()
    
    # Use template structure but replace responses
    result = template_content
    
    # Replace template respondent data with target respondent data
    for target_id, target_resp in target_responses.items():
        if target_id in source_respondents:
            source_id = source_respondents[target_id]
            # Replace the entire response section for this respondent
            pattern = rf'(<respondent id="{re.escape(source_id)}">).*?(</respondent>)'
            replacement = rf'\1\n{target_resp}\n\2'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    
    # Update respondent IDs
    for target_id, source_id in zip(target_responses.keys(), source_respondents.keys()):
        result = result.replace(f'<respondent id="{source_id}">', f'<respondent id="{target_id}">')
    
    return result

def fix_md_file(template_content, target_content, source_respondents, target_responses):
    """Fix Markdown file using template structure"""
    
    # Extract target respondent sections
    target_sections = re.findall(
        r'### Respondent (\d+)\n(.*?)(?=### Respondent|\Z)', 
        target_content, 
        re.DOTALL
    )
    
    target_data = {}
    for resp_id, section_content in target_sections:
        target_data[resp_id] = section_content.strip()
    
    result = template_content
    
    # Replace respondent sections
    for target_id, target_section in target_data.items():
        if target_id in source_respondents:
            source_id = source_respondents[target_id]
            pattern = rf'(### Respondent {re.escape(source_id)}\n).*?(?=### Respondent|\Z)'
            replacement = rf'\1{target_section}\n\n'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    
    # Update respondent IDs in headers
    for target_id, source_id in zip(target_data.keys(), source_respondents.keys()):
        result = result.replace(f'### Respondent {source_id}', f'### Respondent {target_id}')
    
    return result

def fix_txt_file(template_content, target_content, source_respondents, target_respondents):
    """Fix TXT file using template structure"""
    
    # Extract target respondent sections
    target_sections = re.findall(
        r'Respondent (\d+):\n(.*?)(?=Respondent|\Z)', 
        target_content, 
        re.DOTALL
    )
    
    target_data = {}
    for resp_id, section_content in target_sections:
        target_data[resp_id] = section_content.strip()
    
    result = template_content
    
    # Replace respondent sections  
    for target_id, target_section in target_data.items():
        if target_id in source_respondents:
            source_id = source_respondents[target_id]
            pattern = rf'(Respondent {re.escape(source_id)}:\n).*?(?=Respondent|\Z)'
            replacement = rf'\1{target_section}\n\n'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    
    # Update respondent IDs in headers
    for target_id, source_id in zip(target_data.keys(), source_respondents.keys()):
        result = result.replace(f'Respondent {source_id}:', f'Respondent {target_id}:')
    
    return result

def fix_ttl_file(template_content, target_content, source_respondents, target_respondents):
    """Fix TTL file using template structure"""
    
    # Extract target respondent data sections
    target_sections = {}
    
    # Find individual respondent property blocks
    respondent_blocks = re.findall(r':R(\d+) (.*?)(?=:R\d+|\Z)', target_content, re.DOTALL)
    
    for resp_id, block_content in respondent_blocks:
        target_sections[resp_id] = block_content.strip()
    
    result = template_content
    
    # Replace respondent data
    for target_id, target_section in target_sections.items():
        if target_id in source_respondents:
            source_id = source_respondents[target_id]
            
            # Replace the main respondent block
            pattern = rf'(:R{re.escape(source_id)} ).*?(?=:R\d+|\Z)'
            replacement = rf'\g<1>{target_section}\n\n'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
    
    # Update all respondent references
    for target_id, source_id in zip(target_sections.keys(), source_respondents.keys()):
        result = result.replace(f':R{source_id}', f':R{target_id}')
        result = result.replace(f'R{source_id}_', f'R{target_id}_')
    
    return result

def get_respondent_mapping(json_file):
    """Get respondent IDs from JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    respondent_ids = []
    for response in data.get('responses', []):
        respondent_ids.append(str(response.get('respondent', '')))
    
    return respondent_ids

def process_all_cases():
    """Process all case files"""
    
    base_path = Path('benchmark_cache/self-reported-mental-health/answer_lookup')
    formats = ['html', 'xml', 'md', 'txt', 'ttl']
    
    # Source respondent mapping from case_1_modified
    source_respondents = ['73', '85', '129']  # From case_1
    
    print("Processing all case files to fix nested questions...")
    
    for format_name in formats:
        format_dir = base_path / format_name
        if not format_dir.exists():
            continue
            
        print(f"\nProcessing {format_name.upper()} files...")
        
        # Get template file
        template_file = format_dir / f'case_1_modified.{format_name}'
        if not template_file.exists():
            print(f"  Warning: Template file not found: {template_file}")
            continue
        
        # Process all case files
        case_files = sorted(format_dir.glob(f'case_*.{format_name}'))
        
        for case_file in case_files:
            if case_file.name.endswith(f'_modified.{format_name}'):
                continue  # Skip modified files
                
            case_num = case_file.stem.replace('case_', '')
            
            # Get target respondent IDs from JSON
            json_file = base_path / 'json' / f'case_{case_num}.json'
            if not json_file.exists():
                print(f"  Warning: JSON file not found for {case_file.name}")
                continue
                
            target_respondents = get_respondent_mapping(json_file)
            
            # Create mapping between source and target respondents
            respondent_mapping = {}
            for i, target_id in enumerate(target_respondents[:3]):  # Take first 3
                if i < len(source_respondents):
                    respondent_mapping[target_id] = source_respondents[i]
            
            print(f"  Processing {case_file.name} - Respondents: {target_respondents[:3]}")
            
            # Copy template structure with target data
            try:
                fixed_content = copy_template_structure(
                    template_file, case_file, 
                    respondent_mapping, target_respondents
                )
                
                if fixed_content:
                    # Write fixed content back to file
                    with open(case_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"    ✅ Fixed {case_file.name}")
                else:
                    print(f"    ❌ Failed to fix {case_file.name}")
                    
            except Exception as e:
                print(f"    ❌ Error fixing {case_file.name}: {e}")

if __name__ == "__main__":
    process_all_cases()
    print("\nBatch fixing completed!")