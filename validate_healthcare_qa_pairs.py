#!/usr/bin/env python3
"""
Script to validate healthcare-dataset answer_lookup QA pairs against actual questionnaire data.
Checks if the expected_answer in the QA pairs matches the actual data in benchmark_cache.
"""

import json
import os
import re

def load_qa_pairs():
    """Load the QA pairs file"""
    qa_path = '/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_lookup_qa_pairs.json'
    
    with open(qa_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_case_data(case_id):
    """Load the questionnaire data for a specific case"""
    case_path = f'/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_lookup/json/{case_id}.json'
    
    if not os.path.exists(case_path):
        return None
    
    with open(case_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_patient_data(case_data, patient_name):
    """Find patient data by name (case-insensitive)"""
    if not case_data or 'responses' not in case_data:
        return None
    
    patient_name_clean = patient_name.strip().lower()
    
    for response in case_data['responses']:
        if 'answers' in response and 'Name' in response['answers']:
            response_name = response['answers']['Name'].strip().lower()
            if response_name == patient_name_clean:
                return response['answers']
    
    return None

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

def validate_qa_pair(qa_pair):
    """Validate a single QA pair against the actual data"""
    case_id = qa_pair['case_id']
    question = qa_pair['question']
    expected_answer = qa_pair['expected_answer']
    patient_name = qa_pair['metadata']['patient_name']
    
    # Load case data
    case_data = load_case_data(case_id)
    if not case_data:
        return {
            'case_id': case_id,
            'status': 'ERROR',
            'message': f'Case data file not found: {case_id}.json'
        }
    
    # Find patient data
    patient_data = find_patient_data(case_data, patient_name)
    if not patient_data:
        return {
            'case_id': case_id,
            'status': 'ERROR',
            'message': f'Patient not found: {patient_name}'
        }
    
    # Determine what field is being asked for
    question_lower = question.lower()
    
    field_mapping = {
        'billing amount': 'Billing Amount',
        'insurance provider': 'Insurance Provider', 
        'test results': 'Test Results',
        'age': 'Age',
        'gender': 'Gender',
        'blood type': 'Blood Type',
        'medical condition': 'Medical Condition',
        'doctor': 'Doctor',
        'hospital': 'Hospital',
        'room number': 'Room Number',
        'admission type': 'Admission Type',
        'medication': 'Medication',
        'date of admission': 'Date of Admission',
        'discharge date': 'Discharge Date'
    }
    
    field = None
    for key, mapped_field in field_mapping.items():
        if key in question_lower:
            field = mapped_field
            break
    
    if not field:
        return {
            'case_id': case_id,
            'status': 'ERROR',
            'message': f'Could not determine field from question: {question}'
        }
    
    if field not in patient_data:
        return {
            'case_id': case_id,
            'status': 'ERROR', 
            'message': f'Field {field} not found in patient data'
        }
    
    # Get actual value
    actual_raw = patient_data[field]
    
    # Decode if it's an MCQ
    actual_decoded = decode_mcq_answer(case_data['questions'], field, actual_raw)
    
    # Compare with expected answer
    if str(actual_decoded).strip() == str(expected_answer).strip():
        return {
            'case_id': case_id,
            'status': 'VALID',
            'patient_name': patient_name,
            'field': field,
            'expected': expected_answer,
            'actual_raw': actual_raw,
            'actual_decoded': actual_decoded
        }
    else:
        return {
            'case_id': case_id,
            'status': 'INVALID',
            'patient_name': patient_name,
            'field': field,
            'expected': expected_answer,
            'actual_raw': actual_raw,
            'actual_decoded': actual_decoded,
            'message': f'Expected "{expected_answer}" but found "{actual_decoded}"'
        }

def validate_all_qa_pairs():
    """Validate all QA pairs"""
    print("Loading healthcare-dataset QA pairs...")
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
            print(f"   Patient: {result['patient_name']}")
            print(f"   Field: {result['field']} = {result['expected']}")
        elif status == 'INVALID':
            invalid_count += 1
            print(f"❌ {case_id}: INVALID")
            print(f"   Patient: {result['patient_name']}")
            print(f"   Field: {result['field']}")
            print(f"   Expected: {result['expected']}")
            print(f"   Actual (raw): {result['actual_raw']}")
            print(f"   Actual (decoded): {result['actual_decoded']}")
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