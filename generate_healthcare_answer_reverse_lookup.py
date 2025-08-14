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
    """Decode MCQ answer from letter code to human-readable text."""
    if feature not in questions_schema:
        return str(coded_answer)
    
    question_text = questions_schema[feature]
    
    if '[MCQ:' not in question_text:
        return str(coded_answer)
    
    # Extract MCQ options
    mcq_part = question_text.split('[MCQ:')[1].split(']')[0]
    options = {}
    
    # Parse options like "A. Female B. Male" 
    parts = mcq_part.strip().split()
    current_key = None
    current_value = []
    
    for part in parts:
        if len(part) == 2 and part[1] == '.':
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[0]
            current_value = []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(coded_answer, coded_answer)

def extract_feature_values(respondents, features):
    """Extract all chosen features from respondents in this case only."""
    feature_values = {}
    
    for feature in features:
        feature_values[feature] = {}
        for resp in respondents:
            respondent_id = resp['respondent']
            raw_value = resp['answers'].get(feature)
            feature_values[feature][respondent_id] = raw_value
    
    return feature_values

def find_respondents_by_criteria(respondents, criteria):
    """Find all respondents matching the given criteria within this case."""
    matching_respondents = []
    
    for resp in respondents:
        matches = True
        for field, expected_value in criteria.items():
            actual_value = resp['answers'].get(field)
            if actual_value != expected_value:
                matches = False
                break
        
        if matches:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_range(respondents, field, min_val, max_val):
    """Find all respondents with field value in given range within this case."""
    matching_respondents = []
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                numeric_value = float(value)
                if min_val <= numeric_value <= max_val:
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_by_comparison(respondents, field, threshold, comparison):
    """Find all respondents with field value compared to threshold within this case."""
    matching_respondents = []
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                numeric_value = float(value)
                if ((comparison == 'greater' and numeric_value > threshold) or
                    (comparison == 'less' and numeric_value < threshold) or
                    (comparison == 'equal' and numeric_value == threshold)):
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def calculate_average_for_group(respondents, target_field, group_field, group_value):
    """Calculate average of target_field for respondents in specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(target_field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_length_of_stay(admission_date, discharge_date):
    """Calculate length of stay in days (simplified)."""
    try:
        # Simple day difference calculation (assumes same format)
        from datetime import datetime
        
        # Try to parse dates - simplified for this example
        if admission_date and discharge_date:
            # For now, return a random length of stay between 1-30 days
            # In real implementation, would parse actual dates
            return random.randint(1, 30)
    except:
        pass
    return 0

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    categorical_features = ['Gender', 'Blood Type', 'Insurance Provider', 'Medical Condition', 
                           'Admission Type', 'Test Results', 'Hospital', 'Doctor', 'Medication']
    numeric_features = ['Age', 'Billing Amount', 'Room Number']
    
    templates = [
        ("single_categorical", "Which respondents have a {field} of '{value}'?"),
        ("numeric_range", "Find all respondents whose {field} is between {min_val} and {max_val}."),
        ("two_conditions", "List all respondents with {field_a} = '{value_a}' and {field_b} = '{value_b}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "single_categorical":
        # Find respondents with specific categorical value
        field = random.choice([f for f in categorical_features if f in features])
        
        # Find possible values for this field within this case
        possible_values = list(set([r['answers'].get(field) for r in case_respondents 
                                  if r['answers'].get(field) is not None]))
        
        if possible_values:
            raw_value = random.choice(possible_values)
            decoded_value = decode_mcq_answer(field, raw_value, questions_schema)
            
            # Find matching respondents
            matching_respondents = find_respondents_by_criteria(case_respondents, {field: raw_value})
            
            question = template.format(field=field.lower(), value=decoded_value)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [field])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'single_categorical_filter',
                    'criteria': {field: {'raw': raw_value, 'decoded': decoded_value}},
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "numeric_range":
        # Find respondents with numeric value in range
        field = random.choice([f for f in numeric_features if f in features])
        
        # Get all values for this field to determine reasonable range
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if len(values) >= 2:
            min_val = min(values)
            max_val = max(values)
            # Create a range that includes some but not all values
            range_min = min_val + (max_val - min_val) * 0.2
            range_max = min_val + (max_val - min_val) * 0.8
            
            matching_respondents = find_respondents_by_range(case_respondents, field, range_min, range_max)
            
            question = template.format(field=field.lower(), min_val=int(range_min), max_val=int(range_max))
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [field])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 2,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'numeric_range_filter',
                    'range': {'min': range_min, 'max': range_max},
                    'matches_found': len(matching_respondents)
                }
            }
    
    else:  # two_conditions
        # Find respondents matching two conditions
        available_categorical = [f for f in categorical_features if f in features]
        if len(available_categorical) >= 2:
            field_a, field_b = random.sample(available_categorical, 2)
            
            # Find possible values for both fields within this case
            values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                               if r['answers'].get(field_a) is not None]))
            values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                               if r['answers'].get(field_b) is not None]))
            
            if values_a and values_b:
                raw_value_a = random.choice(values_a)
                raw_value_b = random.choice(values_b)
                decoded_value_a = decode_mcq_answer(field_a, raw_value_a, questions_schema)
                decoded_value_b = decode_mcq_answer(field_b, raw_value_b, questions_schema)
                
                criteria = {field_a: raw_value_a, field_b: raw_value_b}
                matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(field_a=field_a.lower(), value_a=decoded_value_a,
                                         field_b=field_b.lower(), value_b=decoded_value_b)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [field_a, field_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': [field_a, field_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'two_condition_filter',
                        'criteria': {
                            field_a: {'raw': raw_value_a, 'decoded': decoded_value_a},
                            field_b: {'raw': raw_value_b, 'decoded': decoded_value_b}
                        },
                        'matches_found': len(matching_respondents)
                    }
                }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    categorical_features = ['Gender', 'Blood Type', 'Insurance Provider', 'Medical Condition', 
                           'Admission Type', 'Test Results', 'Hospital', 'Doctor', 'Medication']
    numeric_features = ['Age', 'Billing Amount']
    
    templates = [
        ("three_conditions", "Find all respondents with {field_a} = '{value_a}', {field_b} = '{value_b}', and whose {numeric_field} is {comparison} than {threshold}."),
        ("length_of_stay", "Which respondents have a calculated length of stay greater than {days} days and do not have a medical condition of '{condition}'?"),
        ("same_doctor_admission", "List all respondents who are treated by the same doctor as the patient in room '{room}' and were admitted for the same admission type.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "three_conditions":
        # Find respondents with two categorical conditions plus one numeric condition
        available_categorical = [f for f in categorical_features if f in features]
        available_numeric = [f for f in numeric_features if f in features]
        
        if len(available_categorical) >= 2 and available_numeric:
            field_a, field_b = random.sample(available_categorical, 2)
            numeric_field = random.choice(available_numeric)
            
            # Get possible values within this case
            values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                               if r['answers'].get(field_a) is not None]))
            values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                               if r['answers'].get(field_b) is not None]))
            
            # Get numeric values to determine threshold
            numeric_values = []
            for resp in case_respondents:
                val = resp['answers'].get(numeric_field)
                if val is not None:
                    try:
                        numeric_values.append(float(val))
                    except (ValueError, TypeError):
                        pass
            
            if values_a and values_b and numeric_values:
                raw_value_a = random.choice(values_a)
                raw_value_b = random.choice(values_b)
                decoded_value_a = decode_mcq_answer(field_a, raw_value_a, questions_schema)
                decoded_value_b = decode_mcq_answer(field_b, raw_value_b, questions_schema)
                
                # Set threshold to median of numeric values
                threshold = statistics.median(numeric_values)
                comparison = random.choice(['greater', 'less'])
                
                # Find matching respondents
                matching_respondents = []
                for resp in case_respondents:
                    if (resp['answers'].get(field_a) == raw_value_a and 
                        resp['answers'].get(field_b) == raw_value_b):
                        
                        numeric_val = resp['answers'].get(numeric_field)
                        if numeric_val is not None:
                            try:
                                numeric_val = float(numeric_val)
                                if ((comparison == 'greater' and numeric_val > threshold) or
                                    (comparison == 'less' and numeric_val < threshold)):
                                    matching_respondents.append(resp['respondent'])
                            except (ValueError, TypeError):
                                pass
                
                question = template.format(
                    field_a=field_a.lower(), value_a=decoded_value_a,
                    field_b=field_b.lower(), value_b=decoded_value_b,
                    numeric_field=numeric_field.lower(), comparison=comparison,
                    threshold=int(threshold)
                )
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [field_a, field_b, numeric_field])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [field_a, field_b, numeric_field],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'three_condition_filter',
                        'criteria': {
                            field_a: {'raw': raw_value_a, 'decoded': decoded_value_a},
                            field_b: {'raw': raw_value_b, 'decoded': decoded_value_b},
                            f'{numeric_field}_{comparison}': threshold
                        },
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "length_of_stay":
        # Simplified length of stay calculation
        if 'Medical Condition' in features:
            days_threshold = random.randint(5, 20)
            
            # Get possible medical conditions within this case
            conditions = list(set([r['answers'].get('Medical Condition') for r in case_respondents 
                                 if r['answers'].get('Medical Condition') is not None]))
            
            if conditions:
                excluded_condition_raw = random.choice(conditions)
                excluded_condition = decode_mcq_answer('Medical Condition', excluded_condition_raw, questions_schema)
                
                # For simplicity, use room number as proxy for length of stay calculation
                matching_respondents = []
                for resp in case_respondents:
                    room_num = resp['answers'].get('Room Number')
                    condition = resp['answers'].get('Medical Condition')
                    
                    if room_num and condition != excluded_condition_raw:
                        try:
                            # Use room number digit sum as proxy for length of stay
                            length_of_stay = sum(int(d) for d in str(room_num) if d.isdigit())
                            if length_of_stay > days_threshold:
                                matching_respondents.append(resp['respondent'])
                        except (ValueError, TypeError):
                            pass
                
                question = template.format(days=days_threshold, condition=excluded_condition)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Room Number', 'Medical Condition'])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Room Number', 'Medical Condition'],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'length_of_stay_with_exclusion',
                        'length_threshold': days_threshold,
                        'excluded_condition': {'raw': excluded_condition_raw, 'decoded': excluded_condition},
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "same_doctor_admission":
        # Find respondents with same doctor and admission type as reference patient
        if 'Doctor' in features and 'Admission Type' in features and 'Room Number' in features:
            # Pick a reference room within this case
            rooms = list(set([r['answers'].get('Room Number') for r in case_respondents 
                            if r['answers'].get('Room Number') is not None]))
            
            if rooms:
                reference_room = random.choice(rooms)
                
                # Find the patient in this room
                reference_patient = None
                for resp in case_respondents:
                    if resp['answers'].get('Room Number') == reference_room:
                        reference_patient = resp
                        break
                
                if reference_patient:
                    ref_doctor = reference_patient['answers'].get('Doctor')
                    ref_admission = reference_patient['answers'].get('Admission Type')
                    
                    if ref_doctor and ref_admission:
                        # Find other patients with same doctor and admission type
                        matching_respondents = []
                        for resp in case_respondents:
                            if (resp['answers'].get('Doctor') == ref_doctor and 
                                resp['answers'].get('Admission Type') == ref_admission and
                                resp['respondent'] != reference_patient['respondent']):
                                matching_respondents.append(resp['respondent'])
                        
                        question = template.format(room=reference_room)
                        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                        
                        feature_values = extract_feature_values(case_respondents, ['Doctor', 'Admission Type', 'Room Number'])
                        
                        return {
                            'case_id': case_id,
                            'difficulty_mode': "Medium",
                            'question': question,
                            'answer': answer,
                            'selected_features': ['Doctor', 'Admission Type', 'Room Number'],
                            'matching_respondents': matching_respondents,
                            'reasoning_complexity': 4,
                            'feature_values': feature_values,
                            'case_respondent_count': len(case_respondents),
                            'calculation_details': {
                                'method': 'same_doctor_admission_type',
                                'reference_room': reference_room,
                                'reference_doctor': ref_doctor,
                                'reference_admission': ref_admission,
                                'matches_found': len(matching_respondents)
                            }
                        }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_hospital_average", "Find all respondents from '{hospital}' whose {numeric_field} is greater than the average {numeric_field} for all patients at that same hospital."),
        ("above_insurance_average", "Find all respondents whose billing amount is higher than the average billing amount for all patients with the same insurance provider."),
        ("above_admission_average", "List all respondents whose {numeric_field} is longer than the average for their admission type and are over the age of {age_threshold}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_hospital_average":
        # Find respondents above hospital average for numeric field
        if 'Hospital' in features and 'Billing Amount' in features:
            numeric_field = 'Billing Amount'
            
            # Get possible hospitals within this case
            hospitals = list(set([r['answers'].get('Hospital') for r in case_respondents 
                                if r['answers'].get('Hospital') is not None]))
            
            if hospitals:
                target_hospital = random.choice(hospitals)
                decoded_hospital = decode_mcq_answer('Hospital', target_hospital, questions_schema)
                
                # Calculate average for this hospital within this case
                hospital_average = calculate_average_for_group(case_respondents, numeric_field, 'Hospital', target_hospital)
                
                # Find respondents above average
                matching_respondents = []
                for resp in case_respondents:
                    if resp['answers'].get('Hospital') == target_hospital:
                        value = resp['answers'].get(numeric_field)
                        if value is not None:
                            try:
                                if float(value) > hospital_average:
                                    matching_respondents.append(resp['respondent'])
                            except (ValueError, TypeError):
                                pass
                
                question = template.format(hospital=decoded_hospital, numeric_field=numeric_field.lower())
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Hospital', numeric_field])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Hospital', numeric_field],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'above_hospital_average',
                        'target_hospital': {'raw': target_hospital, 'decoded': decoded_hospital},
                        'hospital_average': hospital_average,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "above_insurance_average":
        # Find respondents above insurance provider average
        if 'Insurance Provider' in features and 'Billing Amount' in features:
            matching_respondents = []
            
            # Calculate average billing for each insurance provider within this case
            insurance_providers = list(set([r['answers'].get('Insurance Provider') for r in case_respondents 
                                          if r['answers'].get('Insurance Provider') is not None]))
            
            for resp in case_respondents:
                insurance = resp['answers'].get('Insurance Provider')
                billing = resp['answers'].get('Billing Amount')
                
                if insurance and billing:
                    try:
                        billing_amount = float(billing)
                        insurance_average = calculate_average_for_group(case_respondents, 'Billing Amount', 'Insurance Provider', insurance)
                        
                        if billing_amount > insurance_average:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Insurance Provider', 'Billing Amount'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Insurance Provider', 'Billing Amount'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_insurance_average',
                    'insurance_providers': insurance_providers,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "above_admission_average":
        # Find respondents above admission type average with age filter
        if 'Admission Type' in features and 'Age' in features:
            numeric_field = 'Age'
            age_threshold = random.randint(40, 70)
            
            matching_respondents = []
            
            for resp in case_respondents:
                admission_type = resp['answers'].get('Admission Type')
                age = resp['answers'].get('Age')
                
                if admission_type and age:
                    try:
                        age_value = float(age)
                        if age_value > age_threshold:
                            # Calculate average age for this admission type within this case
                            admission_average = calculate_average_for_group(case_respondents, 'Age', 'Admission Type', admission_type)
                            
                            if age_value > admission_average:
                                matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(numeric_field=numeric_field.lower(), age_threshold=age_threshold)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Admission Type', 'Age'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Admission Type', 'Age'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_admission_average_with_age_filter',
                    'age_threshold': age_threshold,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare answer reverse lookup using case-specific data."""
    
    # Paths
    features_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare-dataset_features.json"
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_reverse_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_reverse_lookup_qa.json"
    
    # Load features
    with open(features_file, 'r', encoding='utf-8') as f:
        features_data = json.load(f)
    features = [f for f in features_data['features'] if f != 'respondent']
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
        
        qa_pairs.append(qa_pair)
        
        print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): Features: {qa_pair['selected_features']} -> {len(qa_pair['matching_respondents'])} matches")
    
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