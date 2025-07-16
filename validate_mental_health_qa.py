import json
import os
import glob
from pathlib import Path
from collections import defaultdict

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_nested_value(data, field_path):
    """Get a value from nested dictionaries using dot notation"""
    value = data
    for part in field_path.split('.'):
        if isinstance(value, dict):
            if part in value:
                value = value[part]
            elif 'answers' in value and part in value['answers']:
                value = value['answers'][part]
            else:
                return None
        else:
            return None
    return value

def validate_qa_pairs(task_name):
    print(f"\nValidating {task_name}...")
    
    # Load QA pairs
    qa_pairs_file = f"prompts/self-reported-mental-health/self-reported-mental-health_{task_name}_qa_pairs.json"
    qa_pairs = load_json_file(qa_pairs_file)
    
    # Get all case files from json subdirectory
    case_files = glob.glob(f"benchmark_cache/self-reported-mental-health-college-students-2022/{task_name}/json/case_*.json")
    if not case_files:
        print(f"ERROR: No case files found in benchmark_cache/self-reported-mental-health-college-students-2022/{task_name}/json/")
        return
        
    case_files.sort()
    print(f"Found {len(case_files)} case files")
    
    # Count cases per case_id
    case_counts = defaultdict(int)
    for qa_pair in qa_pairs:
        case_id = qa_pair['case_id']
        case_num = int(case_id.split('_')[1])
        case_counts[case_num] += 1
    
    # Check for missing or extra cases
    missing_cases = []
    for i in range(1, 51):  # Should have cases 1-50
        if i not in case_counts:
            missing_cases.append(i)
    
    if missing_cases:
        print(f"Missing cases: {missing_cases}")
    
    # Count None/empty answers
    none_count = 0
    empty_count = 0
    for qa_pair in qa_pairs:
        if qa_pair['expected_answer'] is None:
            none_count += 1
        elif isinstance(qa_pair['expected_answer'], str) and qa_pair['expected_answer'].strip() == '':
            empty_count += 1
    
    print(f"None answers: {none_count}")
    print(f"Empty answers: {empty_count}")
    
    # Load and validate each case
    all_case_data = {}
    for case_file in case_files:
        case_data = load_json_file(case_file)
        case_num = int(Path(case_file).stem.split('_')[1])
        all_case_data[case_num] = case_data
        
    # Validate answers against case data
    errors = []
    for qa_pair in qa_pairs:
        case_id = qa_pair['case_id']
        case_num = int(case_id.split('_')[1])
        if case_num not in all_case_data:
            continue
            
        case_data = all_case_data[case_num]
        question = qa_pair['prompt']
        answer = qa_pair['expected_answer']
        metadata = qa_pair.get('metadata', {})
        
        # For answer_lookup task, validate the specific field value
        if task_name == 'answer_lookup' and metadata:
            respondent = metadata.get('respondent')
            field = metadata.get('field')
            if respondent and field:
                # Find the respondent in the case data
                for resp in case_data['responses']:
                    if str(resp['respondent']) == str(respondent):
                        # Get the value from nested structure
                        value = get_nested_value(resp, field)
                        if value is not None and str(float(value)) != str(float(answer)):
                            errors.append(f"Case {case_id}: Answer mismatch for respondent {respondent}, field {field}")
                            errors.append(f"  Expected: {answer}")
                            errors.append(f"  Found: {value}")
                        break
        
        # For respondent_count task, validate that the answer is a valid count
        elif task_name == 'respondent_count':
            try:
                count = int(answer)
                if count < 0 or count > len(case_data['responses']):
                    errors.append(f"Case {case_id}: Invalid count {count} - should be between 0 and {len(case_data['responses'])}")
            except ValueError:
                errors.append(f"Case {case_id}: Answer '{answer}' is not a valid count")
        
        # For other tasks, validate that referenced respondents exist
        elif answer and isinstance(answer, str) and any(c.isdigit() for c in answer):
            respondent_ids = [int(x.strip()) for x in answer.replace(',', ' ').split() if x.strip().isdigit()]
            for resp_id in respondent_ids:
                found = False
                for resp in case_data['responses']:
                    if int(resp['respondent']) == resp_id:
                        found = True
                        break
                if not found:
                    errors.append(f"Case {case_id}: Answer '{answer}' references non-existent respondent {resp_id}")
    
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(error)
    else:
        print("\nNo validation errors found")

def main():
    tasks = [
        'answer_lookup',
        'multi_hop_relational_inference', 
        'answer_reverse_lookup',
        'rule_based_querying',
        'respondent_count',
        'conceptual_aggregation'
    ]
    
    for task in tasks:
        validate_qa_pairs(task)

if __name__ == '__main__':
    main() 