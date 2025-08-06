#!/usr/bin/env python3
"""
Script to validate healthcare-dataset answer_reverse_lookup QA pairs against actual questionnaire data.
Checks if the expected_answer (list of patients) matches the actual data when queried by specific field values.
"""

import json
import os
import re

def load_qa_pairs():
    """Load the reverse lookup QA pairs file"""
    qa_path = '/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_reverse_lookup_qa_pairs.json'
    
    with open(qa_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_case_data(case_id):
    """Load the questionnaire data for a specific case"""
    case_path = f'/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_reverse_lookup/json/{case_id}.json'
    
    if not os.path.exists(case_path):
        return None
    
    with open(case_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def decode_mcq_answer(questions, field, coded_answer):
    """Decode MCQ coded answer using the questions schema"""
    if field not in questions:
        return coded_answer
    
    question_text = questions[field]
    
    # Extract MCQ options using regex
    mcq_pattern = r'\[MCQ: (.+?)\]'
    match = re.search(mcq_pattern, question_text)
    
    if not match:
        return coded_answer  # Not an MCQ
    
    options_text = match.group(1)
    
    # Parse options like "A. Aetna B. Blue Cross C. Cigna D. Medicare E. UnitedHealthcare"
    options = {}
    
    # Split by spaces and identify option codes
    parts = options_text.split()
    current_code = None
    current_value = []
    
    for part in parts:
        if len(part) == 2 and part.endswith('.') and part[0].isupper():
            # This is an option code like "A."
            if current_code and current_value:
                options[current_code] = ' '.join(current_value).strip()
            current_code = part[0]
            current_value = []
        else:
            if current_code:
                current_value.append(part)
    
    # Don't forget the last option
    if current_code and current_value:
        options[current_code] = ' '.join(current_value).strip()
    
    return options.get(coded_answer, coded_answer)

def find_patients_with_value(case_data, field, target_value):
    """Find all patients that have a specific value for a given field"""
    if not case_data or 'responses' not in case_data:
        return []
    
    matching_patients = []
    
    for response in case_data['responses']:
        if 'answers' in response and field in response['answers']:
            raw_value = response['answers'][field]
            
            # Decode MCQ if needed
            decoded_value = decode_mcq_answer(case_data['questions'], field, raw_value)
            
            if str(decoded_value).strip().lower() == str(target_value).strip().lower():
                patient_name = response['answers'].get('Name', f'Respondent {response["respondent"]}')
                matching_patients.append(patient_name)
    
    return matching_patients

def parse_field_from_question(question):
    """Parse the field name from the reverse lookup question"""
    question_lower = question.lower()
    
    # Field mapping for common question patterns
    field_mapping = {
        'medical condition': 'Medical Condition',
        'insurance provider': 'Insurance Provider',
        'test results': 'Test Results',
        'blood type': 'Blood Type',
        'admission type': 'Admission Type',
        'taking': 'Medication',  # "Which patient is taking X?"
        'medication': 'Medication',
        'insurance': 'Insurance Provider',  # "Which patient has X insurance?"
        'gender': 'Gender',
        'doctor': 'Doctor',
        'hospital': 'Hospital'
    }
    
    for pattern, field in field_mapping.items():
        if pattern in question_lower:
            return field
    
    return None

def parse_target_value_from_question(question):
    """Parse the target value from the reverse lookup question"""
    # Common patterns:
    # "Which patient has the medical condition Asthma?"
    # "Which patient has Inconclusive test results?"
    # "Which patient has the insurance provider Medicare?"
    # "Which patient is taking Ibuprofen?"
    # "Which patient has Aetna insurance?"
    
    # Try to extract value after common patterns
    patterns = [
        r'has the .+ (.+)\?',           # "has the medical condition Asthma?"
        r'has (.+) .+ results\?',       # "has Inconclusive test results?"
        r'with .+ (.+)\?',              # "with X Y?"
        r'is taking (.+)\?',            # "is taking Ibuprofen?"
        r'has (.+) insurance\?',        # "has Aetna insurance?"
        r'had (.+) admission\?'         # "had Elective admission?"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def normalize_patient_list(patient_list_str):
    """Normalize a comma-separated patient list string"""
    if not patient_list_str:
        return []
    
    # Split by comma and normalize each name
    names = [name.strip() for name in patient_list_str.split(',')]
    return [name for name in names if name]  # Remove empty strings

def compare_patient_lists(expected_list, actual_list):
    """Compare two lists of patient names (case-insensitive)"""
    expected_normalized = [name.strip().lower() for name in expected_list]
    actual_normalized = [name.strip().lower() for name in actual_list]
    
    expected_set = set(expected_normalized)
    actual_set = set(actual_normalized)
    
    return expected_set == actual_set

def validate_qa_pair(qa_pair):
    """Validate a single reverse lookup QA pair against the actual data"""
    case_id = qa_pair['case_id']
    question = qa_pair['question']
    expected_answer = qa_pair['expected_answer']
    metadata = qa_pair.get('metadata', {})
    
    # Load case data
    case_data = load_case_data(case_id)
    if not case_data:
        return {
            'case_id': case_id,
            'status': 'ERROR',
            'message': f'Case data file not found: {case_id}.json'
        }
    
    # Get field and target value from metadata if available, otherwise parse from question
    field = metadata.get('lookup_field')
    target_value = metadata.get('lookup_value')
    
    if not field:
        field = parse_field_from_question(question)
    
    if not target_value:
        target_value = parse_target_value_from_question(question)
    
    if not field:
        return {
            'case_id': case_id,
            'status': 'ERROR',
            'message': f'Could not determine field from question: {question}'
        }
    
    if not target_value:
        return {
            'case_id': case_id,
            'status': 'ERROR', 
            'message': f'Could not determine target value from question: {question}'
        }
    
    # Map field names to actual field names in data
    field_name_mapping = {
        'medical_condition': 'Medical Condition',
        'test_results': 'Test Results',
        'insurance_provider': 'Insurance Provider',
        'blood_type': 'Blood Type',
        'admission_type': 'Admission Type',
        'insurance': 'Insurance Provider',
        'medications': 'Medication',
        'medication': 'Medication'
    }
    
    mapped_field = field_name_mapping.get(field, field)
    
    # Find actual patients with the target value
    actual_patients = find_patients_with_value(case_data, mapped_field, target_value)
    
    # Parse expected patients
    expected_patients = normalize_patient_list(expected_answer)
    
    # Compare the lists
    if compare_patient_lists(expected_patients, actual_patients):
        return {
            'case_id': case_id,
            'status': 'VALID',
            'question': question,
            'field': mapped_field,
            'target_value': target_value,
            'expected_patients': expected_patients,
            'actual_patients': actual_patients
        }
    else:
        return {
            'case_id': case_id,
            'status': 'INVALID',
            'question': question,
            'field': mapped_field,
            'target_value': target_value,
            'expected_patients': expected_patients,
            'actual_patients': actual_patients,
            'message': f'Patient lists don\'t match'
        }

def validate_all_qa_pairs():
    """Validate all reverse lookup QA pairs"""
    print("Loading healthcare-dataset answer_reverse_lookup QA pairs...")
    qa_pairs = load_qa_pairs()
    
    print(f"Found {len(qa_pairs)} QA pairs to validate\\n")
    
    valid_count = 0
    invalid_count = 0
    error_count = 0
    
    for i, qa_pair in enumerate(qa_pairs, 1):
        result = validate_qa_pair(qa_pair)
        
        status = result['status']
        case_id = result['case_id']
        
        if status == 'VALID':
            valid_count += 1
            print(f"✅ {case_id}: VALID")
            print(f"   Question: {result['question']}")
            print(f"   Field: {result['field']} = {result['target_value']}")
            print(f"   Patients: {', '.join(result['expected_patients'])}")
        elif status == 'INVALID':
            invalid_count += 1
            print(f"❌ {case_id}: INVALID")
            print(f"   Question: {result['question']}")
            print(f"   Field: {result['field']} = {result['target_value']}")
            print(f"   Expected: {', '.join(result['expected_patients'])}")
            print(f"   Actual: {', '.join(result['actual_patients'])}")
        else:  # ERROR
            error_count += 1
            print(f"⚠️  {case_id}: ERROR")
            print(f"   Message: {result['message']}")
        
        print()
        
        # Show progress every 10 cases
        if i % 10 == 0:
            print(f"Progress: {i}/{len(qa_pairs)} cases processed...")
            print()
    
    print("="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Total QA pairs: {len(qa_pairs)}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {valid_count/len(qa_pairs)*100:.1f}%")
    
    if invalid_count > 0:
        print(f"\\n⚠️  {invalid_count} QA pairs have incorrect expected answers!")
    
    if error_count > 0:
        print(f"\\n⚠️  {error_count} QA pairs have validation errors!")

if __name__ == "__main__":
    validate_all_qa_pairs()