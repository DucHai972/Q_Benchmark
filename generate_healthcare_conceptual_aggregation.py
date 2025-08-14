#!/usr/bin/env python3
import json
import random
import os
import statistics
from datetime import datetime

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

def calculate_length_of_stay(admission_date, discharge_date):
    """Calculate length of stay in days."""
    try:
        admission = datetime.strptime(admission_date, "%Y-%m-%d")
        discharge = datetime.strptime(discharge_date, "%Y-%m-%d")
        return abs((discharge - admission).days)
    except:
        return None

def count_respondents_by_criteria(respondents, criteria):
    """Count respondents matching the given criteria within this case."""
    count = 0
    
    for resp in respondents:
        matches = True
        for field, expected_value in criteria.items():
            actual_value = resp['answers'].get(field)
            if actual_value != expected_value:
                matches = False
                break
        
        if matches:
            count += 1
    
    return count

def count_respondents_by_numeric_comparison(respondents, field, threshold, comparison='greater'):
    """Count respondents with numeric field compared to threshold within this case."""
    count = 0
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                numeric_value = float(value)
                if ((comparison == 'greater' and numeric_value > threshold) or
                    (comparison == 'less' and numeric_value < threshold) or
                    (comparison == 'equal' and numeric_value == threshold) or
                    (comparison == 'greater_equal' and numeric_value >= threshold) or
                    (comparison == 'less_equal' and numeric_value <= threshold)):
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_by_length_of_stay(respondents, min_days, max_days):
    """Count respondents with length of stay in given range within this case."""
    count = 0
    
    for resp in respondents:
        admission = resp['answers'].get('Date of Admission')
        discharge = resp['answers'].get('Discharge Date')
        
        if admission and discharge:
            los = calculate_length_of_stay(admission, discharge)
            if los is not None and min_days <= los <= max_days:
                count += 1
    
    return count

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

def calculate_average_los_for_admission_type(respondents, admission_type):
    """Calculate average length of stay for specific admission type within this case."""
    type_respondents = [r for r in respondents if r['answers'].get('Admission Type') == admission_type]
    
    los_values = []
    for resp in type_respondents:
        admission = resp['answers'].get('Date of Admission')
        discharge = resp['answers'].get('Discharge Date')
        
        if admission and discharge:
            los = calculate_length_of_stay(admission, discharge)
            if los is not None:
                los_values.append(los)
    
    return statistics.mean(los_values) if los_values else 0

def count_patients_with_condition(respondents, condition_code):
    """Count patients with specific medical condition within this case."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('Medical Condition') == condition_code:
            count += 1
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    templates = [
        ("single_categorical", "How many respondents have a {field} of '{value}'?"),
        ("single_numeric", "Count the respondents whose {field} is greater than {threshold}."),
        ("two_criteria", "How many respondents have {field_a} = '{value_a}' and {field_b} = '{value_b}'?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "single_categorical":
        # Count by single categorical field
        categorical_fields = ['Gender', 'Blood Type', 'Medical Condition', 
                             'Insurance Provider', 'Admission Type', 'Medication', 'Test Results']
        field = random.choice(categorical_fields)
        
        # Get possible values for this field within this case
        possible_values = list(set([r['answers'].get(field) for r in case_respondents 
                                   if r['answers'].get(field) is not None]))
        
        if possible_values:
            raw_value = random.choice(possible_values)
            decoded_value = decode_mcq_answer(field, raw_value, questions_schema)
            
            count = count_respondents_by_criteria(case_respondents, {field: raw_value})
            
            question = template.format(field=field, value=decoded_value)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'single_categorical_count',
                    'criteria': {field: {'raw': raw_value, 'decoded': decoded_value}},
                    'count': count
                }
            }
    
    elif template_type == "single_numeric":
        # Count by single numeric comparison
        numeric_fields = ['Age', 'Billing Amount']
        field = random.choice(numeric_fields)
        
        # Get values and choose reasonable threshold
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if values:
            if field == 'Age':
                threshold = random.choice([40, 50, 60, 65])
            else:  # Billing Amount
                threshold = random.choice([10000, 20000, 30000, 40000])
            
            count = count_respondents_by_numeric_comparison(case_respondents, field, threshold, 'greater')
            
            question = template.format(field=field, threshold=int(threshold))
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'single_numeric_comparison',
                    'field': field,
                    'threshold': threshold,
                    'comparison': 'greater',
                    'count': count
                }
            }
    
    else:  # two_criteria
        # Count by two criteria
        field_a = 'Gender'
        field_b = random.choice(['Medical Condition', 'Admission Type', 'Insurance Provider'])
        
        # Get possible values within this case
        values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                           if r['answers'].get(field_a) is not None]))
        values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                           if r['answers'].get(field_b) is not None]))
        
        if values_a and values_b:
            raw_value_a = random.choice(values_a)
            raw_value_b = random.choice(values_b)
            
            decoded_value_a = decode_mcq_answer(field_a, raw_value_a, questions_schema)
            decoded_value_b = decode_mcq_answer(field_b, raw_value_b, questions_schema)
            
            count = count_respondents_by_criteria(case_respondents, {field_a: raw_value_a, field_b: raw_value_b})
            
            question = template.format(field_a=field_a, value_a=decoded_value_a,
                                     field_b=field_b, value_b=decoded_value_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field_a, field_b],
                'count': count,
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'two_criteria_count',
                    'criteria': {
                        field_a: {'raw': raw_value_a, 'decoded': decoded_value_a},
                        field_b: {'raw': raw_value_b, 'decoded': decoded_value_b}
                    },
                    'count': count
                }
            }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("three_criteria", "How many respondents with {field_a} = '{value_a}' and {field_b} = '{value_b}' have a {numeric_field} below {threshold}?"),
        ("los_range", "Count the respondents whose length of stay is between {min_days} and {max_days} days and who were admitted for an '{admission_type}' procedure."),
        ("hospital_age_no_med", "How many respondents from '{hospital}' are over the age of {age} and are not taking '{medication}'?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "three_criteria":
        # Count with three criteria including numeric comparison
        field_a = 'Gender'
        field_b = 'Admission Type'
        numeric_field = 'Billing Amount'
        
        # Get possible values within this case
        values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                           if r['answers'].get(field_a) is not None]))
        values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                           if r['answers'].get(field_b) is not None]))
        
        if values_a and values_b:
            raw_value_a = random.choice(values_a)
            raw_value_b = random.choice(values_b)
            threshold = random.choice([20000, 30000, 40000])
            
            decoded_value_a = decode_mcq_answer(field_a, raw_value_a, questions_schema)
            decoded_value_b = decode_mcq_answer(field_b, raw_value_b, questions_schema)
            
            # Count respondents matching all criteria
            count = 0
            for resp in case_respondents:
                if (resp['answers'].get(field_a) == raw_value_a and
                    resp['answers'].get(field_b) == raw_value_b):
                    billing = resp['answers'].get(numeric_field)
                    if billing is not None:
                        try:
                            if float(billing) < threshold:
                                count += 1
                        except (ValueError, TypeError):
                            pass
            
            question = template.format(field_a=field_a, value_a=decoded_value_a,
                                     field_b=field_b, value_b=decoded_value_b,
                                     numeric_field=numeric_field, threshold=threshold)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [field_a, field_b, numeric_field],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'three_criteria_count',
                    'criteria': {
                        field_a: {'raw': raw_value_a, 'decoded': decoded_value_a},
                        field_b: {'raw': raw_value_b, 'decoded': decoded_value_b},
                        f'{numeric_field}_below': threshold
                    },
                    'count': count
                }
            }
    
    elif template_type == "los_range":
        # Count by length of stay range and admission type
        admission_types = list(set([r['answers'].get('Admission Type') for r in case_respondents 
                                  if r['answers'].get('Admission Type') is not None]))
        
        if admission_types:
            admission_type_code = random.choice(admission_types)
            admission_type_text = decode_mcq_answer('Admission Type', admission_type_code, questions_schema)
            
            min_days = random.choice([5, 10, 15])
            max_days = min_days + random.choice([10, 20, 30])
            
            # Count respondents matching criteria
            count = 0
            for resp in case_respondents:
                if resp['answers'].get('Admission Type') == admission_type_code:
                    admission = resp['answers'].get('Date of Admission')
                    discharge = resp['answers'].get('Discharge Date')
                    
                    if admission and discharge:
                        los = calculate_length_of_stay(admission, discharge)
                        if los is not None and min_days <= los <= max_days:
                            count += 1
            
            question = template.format(min_days=min_days, max_days=max_days,
                                     admission_type=admission_type_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Date of Admission', 'Discharge Date', 'Admission Type'],
                'count': count,
                'reasoning_complexity': 4,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'los_range_admission_type',
                    'los_range': [min_days, max_days],
                    'admission_type': {'raw': admission_type_code, 'decoded': admission_type_text},
                    'count': count
                }
            }
    
    elif template_type == "hospital_age_no_med":
        # Count from specific hospital, over age, not taking specific medication
        hospitals = list(set([r['answers'].get('Hospital') for r in case_respondents 
                           if r['answers'].get('Hospital') is not None]))
        medications = list(set([r['answers'].get('Medication') for r in case_respondents 
                              if r['answers'].get('Medication') is not None]))
        
        if hospitals and medications:
            hospital = random.choice(hospitals)
            medication_code = random.choice(medications)
            medication_text = decode_mcq_answer('Medication', medication_code, questions_schema)
            age_threshold = random.choice([50, 60, 65])
            
            # Count respondents matching criteria
            count = 0
            for resp in case_respondents:
                if (resp['answers'].get('Hospital') == hospital and
                    resp['answers'].get('Medication') != medication_code):
                    age = resp['answers'].get('Age')
                    if age is not None:
                        try:
                            if float(age) > age_threshold:
                                count += 1
                        except (ValueError, TypeError):
                            pass
            
            question = template.format(hospital=hospital, age=age_threshold,
                                     medication=medication_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Hospital', 'Age', 'Medication'],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'hospital_age_no_medication',
                    'hospital': hospital,
                    'age_threshold': age_threshold,
                    'excluded_medication': {'raw': medication_code, 'decoded': medication_text},
                    'count': count
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_group_average", "How many respondents have a {numeric_field} that is higher than the average {numeric_field} for their {grouping_field}?"),
        ("condition_comparison", "Count the respondents who are in a hospital where the number of patients with {condition_a} is greater than the number of patients with {condition_b}."),
        ("los_above_admission_avg", "How many respondents over the age of {age} have a length of stay that is longer than the average for their specific {field}?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_group_average":
        # Count respondents above their group average
        numeric_field = 'Billing Amount'
        grouping_field = 'Admission Type'
        
        # Calculate averages by group within this case
        groups = list(set([r['answers'].get(grouping_field) for r in case_respondents 
                         if r['answers'].get(grouping_field) is not None]))
        
        group_averages = {}
        for group in groups:
            avg = calculate_average_for_group(case_respondents, numeric_field, grouping_field, group)
            group_averages[group] = avg
        
        # Count respondents above their group average
        count = 0
        for resp in case_respondents:
            group = resp['answers'].get(grouping_field)
            value = resp['answers'].get(numeric_field)
            
            if group and value is not None and group in group_averages:
                try:
                    if float(value) > group_averages[group]:
                        count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template.format(numeric_field=numeric_field, grouping_field=grouping_field)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [numeric_field, grouping_field],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_group_average',
                'numeric_field': numeric_field,
                'grouping_field': grouping_field,
                'group_averages': {decode_mcq_answer(grouping_field, k, questions_schema): v 
                                  for k, v in group_averages.items()},
                'count': count
            }
        }
    
    elif template_type == "condition_comparison":
        # Count respondents in hospitals where condition A > condition B
        conditions = list(set([r['answers'].get('Medical Condition') for r in case_respondents 
                            if r['answers'].get('Medical Condition') is not None]))
        
        if len(conditions) >= 2:
            condition_a_code, condition_b_code = random.sample(conditions, 2)
            condition_a_text = decode_mcq_answer('Medical Condition', condition_a_code, questions_schema)
            condition_b_text = decode_mcq_answer('Medical Condition', condition_b_code, questions_schema)
            
            # Count conditions by hospital within this case
            hospitals = list(set([r['answers'].get('Hospital') for r in case_respondents 
                               if r['answers'].get('Hospital') is not None]))
            
            qualifying_hospitals = []
            for hospital in hospitals:
                hosp_respondents = [r for r in case_respondents if r['answers'].get('Hospital') == hospital]
                count_a = sum(1 for r in hosp_respondents if r['answers'].get('Medical Condition') == condition_a_code)
                count_b = sum(1 for r in hosp_respondents if r['answers'].get('Medical Condition') == condition_b_code)
                
                if count_a > count_b:
                    qualifying_hospitals.append(hospital)
            
            # Count respondents in qualifying hospitals
            count = sum(1 for r in case_respondents if r['answers'].get('Hospital') in qualifying_hospitals)
            
            question = template.format(condition_a=condition_a_text, condition_b=condition_b_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Hospital', 'Medical Condition'],
                'count': count,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'hospital_condition_comparison',
                    'condition_a': {'raw': condition_a_code, 'decoded': condition_a_text},
                    'condition_b': {'raw': condition_b_code, 'decoded': condition_b_text},
                    'qualifying_hospitals': qualifying_hospitals,
                    'count': count
                }
            }
    
    elif template_type == "los_above_admission_avg":
        # Count older respondents with LOS above their admission type average
        age_threshold = random.choice([50, 60, 65])
        field = 'Admission Type'
        
        # Calculate average LOS by admission type within this case
        admission_types = list(set([r['answers'].get(field) for r in case_respondents 
                                  if r['answers'].get(field) is not None]))
        
        admission_averages = {}
        for admission_type in admission_types:
            avg_los = calculate_average_los_for_admission_type(case_respondents, admission_type)
            admission_averages[admission_type] = avg_los
        
        # Count respondents matching criteria
        count = 0
        for resp in case_respondents:
            age = resp['answers'].get('Age')
            admission_type = resp['answers'].get(field)
            admission = resp['answers'].get('Date of Admission')
            discharge = resp['answers'].get('Discharge Date')
            
            if age is not None and admission_type and admission and discharge:
                try:
                    if float(age) > age_threshold:
                        los = calculate_length_of_stay(admission, discharge)
                        if los is not None and admission_type in admission_averages:
                            if los > admission_averages[admission_type]:
                                count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template.format(age=age_threshold, field=field)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Age', 'Date of Admission', 'Discharge Date', field],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'los_above_admission_type_average',
                'age_threshold': age_threshold,
                'admission_type_averages': {decode_mcq_answer(field, k, questions_schema): v 
                                           for k, v in admission_averages.items()},
                'count': count
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare conceptual aggregation using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/conceptual_aggregation/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_conceptual_aggregation_qa.json"
    
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
        
        qa_pairs.append(qa_pair)
        
        print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): Count = {qa_pair['count']}")
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs using case-specific data")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    difficulty_counts = {}
    respondent_counts = []
    answer_counts = []
    
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        respondent_counts.append(pair['case_respondent_count'])
        answer_counts.append(pair['count'])
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n👥 Respondent counts per case:")
    print(f"  Average: {sum(respondent_counts)/len(respondent_counts):.1f} respondents per case")
    print(f"  Range: {min(respondent_counts)} - {max(respondent_counts)} respondents")
    
    print(f"\n🎯 Answer counts per question:")
    print(f"  Average: {sum(answer_counts)/len(answer_counts):.1f} count per question")
    print(f"  Range: {min(answer_counts)} - {max(answer_counts)} count")

if __name__ == "__main__":
    main()