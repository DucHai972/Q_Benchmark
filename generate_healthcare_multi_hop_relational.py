#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def decode_mcq_answer(feature, coded_answer, questions_schema):
    """Decode MCQ answer from coded value to human-readable text."""
    if feature not in questions_schema:
        return str(coded_answer)
    
    question_text = questions_schema[feature]
    
    if '[MCQ:' not in question_text:
        return str(coded_answer)
    
    # Extract MCQ options
    mcq_part = question_text.split('[MCQ:')[1].split(']')[0]
    options = {}
    
    # Parse options like "A. Option1 B. Option2"
    parts = mcq_part.strip().split(' ')
    current_key = None
    current_value = []
    
    for part in parts:
        if part and len(part) > 1 and part[1] == '.':
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[0]
            current_value = [part[2:]] if len(part) > 2 else []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(coded_answer, str(coded_answer))

def find_respondents_with_same_feature(respondents, target_respondent_id, feature, exclude_self=True):
    """Find all respondents who share the same feature value as the target respondent within this case."""
    # Find the target respondent's value for this feature
    target_value = None
    for resp in respondents:
        if resp['respondent'] == target_respondent_id:
            target_value = resp['answers'].get(feature)
            break
    
    if target_value is None:
        return []
    
    # Find all respondents with the same value
    matching_respondents = []
    for resp in respondents:
        if resp['answers'].get(feature) == target_value:
            if not exclude_self or resp['respondent'] != target_respondent_id:
                matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_with_same_feature_and_condition(respondents, target_respondent_id, shared_feature, condition_field, condition_value, condition_comparison='equal'):
    """Find respondents who share a feature with target and meet an additional condition within this case."""
    # First find respondents with same feature
    same_feature_respondents = find_respondents_with_same_feature(respondents, target_respondent_id, shared_feature, exclude_self=True)
    
    # Filter by additional condition
    matching_respondents = []
    for resp_id in same_feature_respondents:
        for resp in respondents:
            if resp['respondent'] == resp_id:
                value = resp['answers'].get(condition_field)
                if value is not None:
                    if condition_comparison == 'equal' and value == condition_value:
                        matching_respondents.append(resp_id)
                    elif condition_comparison == 'greater':
                        try:
                            if float(value) > condition_value:
                                matching_respondents.append(resp_id)
                        except (ValueError, TypeError):
                            pass
                    elif condition_comparison == 'different' and value != condition_value:
                        matching_respondents.append(resp_id)
                break
    
    return matching_respondents

def calculate_average_for_doctor_group(respondents, doctor_name, field):
    """Calculate average of field for all patients treated by specific doctor within this case."""
    doctor_patients = [r for r in respondents if r['answers'].get('Doctor') == doctor_name]
    
    values = []
    for resp in doctor_patients:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_age_by_hospital(respondents):
    """Calculate average age for each hospital within this case."""
    hospital_ages = {}
    
    # Group by hospital
    hospitals = {}
    for resp in respondents:
        hospital = resp['answers'].get('Hospital')
        if hospital:
            if hospital not in hospitals:
                hospitals[hospital] = []
            hospitals[hospital].append(resp)
    
    # Calculate averages
    for hospital, hospital_respondents in hospitals.items():
        ages = []
        for resp in hospital_respondents:
            age = resp['answers'].get('Age')
            if age is not None:
                try:
                    ages.append(float(age))
                except (ValueError, TypeError):
                    pass
        
        hospital_ages[hospital] = statistics.mean(ages) if ages else 0
    
    return hospital_ages

def find_youngest_patient_with_condition(respondents, condition_code):
    """Find the youngest patient with specific medical condition within this case."""
    condition_patients = [r for r in respondents if r['answers'].get('Medical Condition') == condition_code]
    
    if not condition_patients:
        return None
    
    youngest_patient = None
    youngest_age = float('inf')
    
    for resp in condition_patients:
        age = resp['answers'].get('Age')
        if age is not None:
            try:
                age_num = float(age)
                if age_num < youngest_age:
                    youngest_age = age_num
                    youngest_patient = resp
            except (ValueError, TypeError):
                pass
    
    return youngest_patient

def find_patient_with_highest_billing(respondents):
    """Find the patient with highest billing amount within this case."""
    highest_patient = None
    highest_billing = 0
    
    for resp in respondents:
        billing = resp['answers'].get('Billing Amount')
        if billing is not None:
            try:
                billing_num = float(billing)
                if billing_num > highest_billing:
                    highest_billing = billing_num
                    highest_patient = resp
            except (ValueError, TypeError):
                pass
    
    return highest_patient

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Features that can be shared between patients
    shareable_features = ['Hospital', 'Insurance Provider', 'Doctor', 'Admission Type', 'Medical Condition', 'Medication']
    
    templates = [
        ("same_hospital", "Which respondents are in the same hospital as respondent '{target_id}'?"),
        ("same_insurance", "Find all respondents with the same insurance provider as respondent '{target_id}', excluding the respondent themselves."),
        ("same_doctor", "List all respondents who are treated by the same doctor as respondent '{target_id}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "same_hospital":
        feature = 'Hospital'
        matching_respondents = find_respondents_with_same_feature(case_respondents, target_id, feature, exclude_self=True)
        
        question = template.format(target_id=target_id)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [feature],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 2,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_hop',
                'target_respondent': target_id,
                'shared_feature': feature,
                'target_feature_value': target_respondent['answers'].get(feature),
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "same_insurance":
        feature = 'Insurance Provider'
        matching_respondents = find_respondents_with_same_feature(case_respondents, target_id, feature, exclude_self=True)
        
        question = template.format(target_id=target_id)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [feature],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 2,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_hop_exclude_self',
                'target_respondent': target_id,
                'shared_feature': feature,
                'target_feature_value': target_respondent['answers'].get(feature),
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # same_doctor
        feature = 'Doctor'
        matching_respondents = find_respondents_with_same_feature(case_respondents, target_id, feature, exclude_self=True)
        
        question = template.format(target_id=target_id)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [feature],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 2,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_hop',
                'target_respondent': target_id,
                'shared_feature': feature,
                'target_feature_value': target_respondent['answers'].get(feature),
                'matches_found': len(matching_respondents)
            }
        }

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("hospital_billing", "Which respondents are in the same hospital as respondent '{target_id}' and also have a 'Billing Amount' over {threshold}?"),
        ("doctor_test_results", "Find all respondents who are treated by the same doctor as respondent '{target_id}' and who have '{test_result}' test results."),
        ("admission_different_gender", "List all respondents who have the same 'Admission Type' as respondent '{target_id}' but are a different gender.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "hospital_billing":
        shared_feature = 'Hospital'
        condition_field = 'Billing Amount'
        threshold = random.choice([20000, 30000, 40000, 50000])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, threshold, 'greater'
        )
        
        question = template.format(target_id=target_id, threshold=threshold)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [shared_feature, condition_field],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_plus_condition',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'condition_field': condition_field,
                'condition_threshold': threshold,
                'condition_comparison': 'greater',
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "doctor_test_results":
        shared_feature = 'Doctor'
        condition_field = 'Test Results'
        test_result_codes = ['A', 'B', 'C']  # Abnormal, Inconclusive, Normal
        test_result_code = random.choice(test_result_codes)
        test_result_text = decode_mcq_answer(condition_field, test_result_code, questions_schema)
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, test_result_code, 'equal'
        )
        
        question = template.format(target_id=target_id, test_result=test_result_text)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [shared_feature, condition_field],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_plus_condition',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'condition_field': condition_field,
                'condition_value': {'raw': test_result_code, 'decoded': test_result_text},
                'condition_comparison': 'equal',
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # admission_different_gender
        shared_feature = 'Admission Type'
        condition_field = 'Gender'
        target_gender = target_respondent['answers'].get(condition_field)
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, target_gender, 'different'
        )
        
        question = template.format(target_id=target_id)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [shared_feature, condition_field],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_different_condition',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'condition_field': condition_field,
                'target_condition_value': target_gender,
                'condition_comparison': 'different',
                'matches_found': len(matching_respondents)
            }
        }

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("billing_above_doctor_avg", "Find all respondents whose billing amount is higher than the average for all patients treated by the same doctor as respondent '{target_id}'."),
        ("hospital_below_avg_age", "Which respondents are from a hospital where the average age of patients is lower than the overall average age of all respondents?"),
        ("same_medication_youngest_cancer", "List all respondents who are taking the same medication as the youngest patient with '{condition}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    if template_type == "billing_above_doctor_avg":
        target_respondent = random.choice(case_respondents)
        target_id = target_respondent['respondent']
        target_doctor = target_respondent['answers'].get('Doctor')
        
        if target_doctor:
            # Calculate average billing for patients of this doctor
            doctor_avg_billing = calculate_average_for_doctor_group(case_respondents, target_doctor, 'Billing Amount')
            
            # Find respondents above this average
            matching_respondents = []
            for resp in case_respondents:
                billing = resp['answers'].get('Billing Amount')
                if billing is not None:
                    try:
                        if float(billing) > doctor_avg_billing:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(target_id=target_id)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Doctor', 'Billing Amount'],
                'target_respondent': target_id,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'billing_above_doctor_average',
                    'target_respondent': target_id,
                    'target_doctor': target_doctor,
                    'doctor_average_billing': doctor_avg_billing,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "hospital_below_avg_age":
        # Calculate overall average age
        all_ages = []
        for resp in case_respondents:
            age = resp['answers'].get('Age')
            if age is not None:
                try:
                    all_ages.append(float(age))
                except (ValueError, TypeError):
                    pass
        
        if all_ages:
            overall_avg_age = statistics.mean(all_ages)
            
            # Calculate average age by hospital
            hospital_ages = calculate_average_age_by_hospital(case_respondents)
            
            # Find hospitals with below average age
            qualifying_hospitals = [hosp for hosp, avg_age in hospital_ages.items() if avg_age < overall_avg_age]
            
            # Find all respondents in these hospitals
            matching_respondents = []
            for resp in case_respondents:
                hospital = resp['answers'].get('Hospital')
                if hospital in qualifying_hospitals:
                    matching_respondents.append(resp['respondent'])
            
            question = template
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Hospital', 'Age'],
                'target_respondent': None,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'hospital_below_average_age',
                    'overall_average_age': overall_avg_age,
                    'hospital_averages': hospital_ages,
                    'qualifying_hospitals': qualifying_hospitals,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "same_medication_youngest_cancer":
        condition_codes = ['A', 'B', 'C', 'D', 'E', 'F']  # Different medical conditions
        condition_code = random.choice(condition_codes)
        condition_text = decode_mcq_answer('Medical Condition', condition_code, questions_schema)
        
        # Find youngest patient with this condition
        youngest_patient = find_youngest_patient_with_condition(case_respondents, condition_code)
        
        if youngest_patient:
            youngest_medication = youngest_patient['answers'].get('Medication')
            
            # Find all respondents with same medication
            matching_respondents = []
            for resp in case_respondents:
                if resp['answers'].get('Medication') == youngest_medication:
                    matching_respondents.append(resp['respondent'])
            
            question = template.format(condition=condition_text)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Medical Condition', 'Age', 'Medication'],
                'target_respondent': youngest_patient['respondent'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'same_medication_youngest_condition',
                    'target_condition': {'raw': condition_code, 'decoded': condition_text},
                    'youngest_patient': youngest_patient['respondent'],
                    'youngest_age': youngest_patient['answers'].get('Age'),
                    'target_medication': youngest_medication,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare multi hop relational inference using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/multi_hop_relational_inference/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_multi_hop_relational_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names
    features = list(sample_data['questions'].keys())
    print(f"Loaded {len(features)} features")
    
    # Generate Q&A pairs
    qa_pairs = []
    
    for i in range(1, 51):
        case_id = f"case_{i}"
        case_file = os.path.join(data_dir, f"{case_id}.json")
        
        if not os.path.exists(case_file):
            print(f"Warning: {case_file} not found, skipping...")
            continue
        
        # Load ONLY this specific case
        case_data = load_case_data(case_file)
        case_respondents = case_data['responses']
        questions_schema = case_data['questions']
        
        print(f"Processing {case_id} with {len(case_respondents)} respondents...")
        
        # Determine difficulty mode and generate question
        if i <= 25:
            qa_pair = generate_easy_question(case_id, case_respondents, features, questions_schema)
        elif i <= 40:
            qa_pair = generate_medium_question(case_id, case_respondents, features, questions_schema)
        else:
            qa_pair = generate_hard_question(case_id, case_respondents, features, questions_schema)
        
        if qa_pair:
            qa_pairs.append(qa_pair)
            print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): {len(qa_pair['matching_respondents'])} matches")
        else:
            print(f"Failed to generate question for {case_id}")
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs using case-specific data")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    difficulty_counts = {}
    respondent_counts = []
    match_counts = []
    
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        respondent_counts.append(pair['case_respondent_count'])
        match_counts.append(len(pair['matching_respondents']))
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n👥 Respondent counts per case:")
    print(f"  Average: {sum(respondent_counts)/len(respondent_counts):.1f} respondents per case")
    print(f"  Range: {min(respondent_counts)} - {max(respondent_counts)} respondents")
    
    print(f"\n🎯 Matching respondents per question:")
    print(f"  Average: {sum(match_counts)/len(match_counts):.1f} matches per question")
    print(f"  Range: {min(match_counts)} - {max(match_counts)} matches")

if __name__ == "__main__":
    main()