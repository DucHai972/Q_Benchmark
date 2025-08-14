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
        admit_dt = datetime.strptime(admission_date, '%Y-%m-%d')
        discharge_dt = datetime.strptime(discharge_date, '%Y-%m-%d')
        return abs((discharge_dt - admit_dt).days)
    except (ValueError, TypeError):
        return None

def find_respondents_with_numerical_rule(respondents, field, threshold, comparison):
    """Find respondents meeting numerical rule."""
    matching_respondents = []
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                num_value = float(value)
                
                if comparison == 'greater' and num_value > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and num_value < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and num_value == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'between' and isinstance(threshold, tuple):
                    min_val, max_val = threshold
                    if min_val <= num_value <= max_val:
                        matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_categorical_and_numerical_rule(respondents, cat_field, cat_value, num_field, threshold, comparison):
    """Find respondents meeting both categorical and numerical rules."""
    matching_respondents = []
    
    for resp in respondents:
        cat_val = resp['answers'].get(cat_field)
        num_val = resp['answers'].get(num_field)
        
        if cat_val == cat_value and num_val is not None:
            try:
                num_value = float(num_val)
                
                if comparison == 'greater' and num_value > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and num_value < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and num_value == threshold:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_length_of_stay_rule(respondents, threshold, comparison):
    """Find respondents meeting length of stay rule."""
    matching_respondents = []
    
    for resp in respondents:
        admission_date = resp['answers'].get('Date of Admission')
        discharge_date = resp['answers'].get('Discharge Date')
        
        if admission_date and discharge_date:
            los = calculate_length_of_stay(admission_date, discharge_date)
            if los is not None:
                if comparison == 'greater' and los > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and los < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and los == threshold:
                    matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_with_multiple_rules(respondents, conditions):
    """Find respondents meeting multiple conditions."""
    matching_respondents = []
    
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in conditions:
            field = condition['field']
            value = condition.get('value')
            threshold = condition.get('threshold')
            comparison = condition.get('comparison', 'equal')
            
            resp_value = resp['answers'].get(field)
            
            if comparison == 'equal':
                if resp_value != value:
                    meets_all_conditions = False
                    break
            elif comparison in ['greater', 'less']:
                if resp_value is None:
                    meets_all_conditions = False
                    break
                try:
                    resp_num = float(resp_value)
                    thresh_num = float(threshold)
                    
                    if comparison == 'greater' and resp_num <= thresh_num:
                        meets_all_conditions = False
                        break
                    elif comparison == 'less' and resp_num >= thresh_num:
                        meets_all_conditions = False
                        break
                except (ValueError, TypeError):
                    meets_all_conditions = False
                    break
            elif comparison == 'even':
                try:
                    resp_num = float(resp_value)
                    if resp_num % 2 != 0:
                        meets_all_conditions = False
                        break
                except (ValueError, TypeError):
                    meets_all_conditions = False
                    break
        
        if meets_all_conditions:
            matching_respondents.append(resp)
    
    return matching_respondents

def calculate_average_for_group(respondents, group_field, group_value, value_field):
    """Calculate average value for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        val = resp['answers'].get(value_field)
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_length_of_stay_for_group(respondents, group_field, group_value):
    """Calculate average length of stay for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    lengths = []
    for resp in group_respondents:
        admission_date = resp['answers'].get('Date of Admission')
        discharge_date = resp['answers'].get('Discharge Date')
        
        if admission_date and discharge_date:
            los = calculate_length_of_stay(admission_date, discharge_date)
            if los is not None:
                lengths.append(los)
    
    return statistics.mean(lengths) if lengths else 0

def find_respondents_above_group_average(respondents, group_field, value_field):
    """Find respondents with value above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_value = resp['answers'].get(value_field)
        
        if resp_group and resp_value is not None:
            try:
                resp_num = float(resp_value)
                group_avg = calculate_average_for_group(respondents, group_field, resp_group, value_field)
                
                if resp_num > group_avg:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_los_above_group_average(respondents, group_field):
    """Find respondents with length of stay above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        admission_date = resp['answers'].get('Date of Admission')
        discharge_date = resp['answers'].get('Discharge Date')
        
        if resp_group and admission_date and discharge_date:
            resp_los = calculate_length_of_stay(admission_date, discharge_date)
            if resp_los is not None:
                group_avg_los = calculate_average_length_of_stay_for_group(respondents, group_field, resp_group)
                
                if resp_los > group_avg_los:
                    matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_with_los_multiple_of_group_average(respondents, group_field, multiplier):
    """Find respondents with length of stay that is multiple of their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        admission_date = resp['answers'].get('Date of Admission')
        discharge_date = resp['answers'].get('Discharge Date')
        
        if resp_group and admission_date and discharge_date:
            resp_los = calculate_length_of_stay(admission_date, discharge_date)
            if resp_los is not None:
                group_avg_los = calculate_average_length_of_stay_for_group(respondents, group_field, resp_group)
                
                if group_avg_los > 0 and resp_los > multiplier * group_avg_los:
                    matching_respondents.append(resp)
    
    return matching_respondents

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Numerical fields that can be used for rules
    numerical_fields = ['Age', 'Billing Amount']
    
    templates = [
        ("numerical_greater", "Which respondents have a '{field}' greater than {threshold}?"),
        ("numerical_between", "Find all respondents whose '{field}' is between {min_val} and {max_val}."),
        ("categorical_numerical", "List all {category} respondents whose '{field}' is less than {threshold}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "numerical_greater":
        field = random.choice(numerical_fields)
        
        # Get sample values to set reasonable threshold
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if values:
            threshold = random.choice([statistics.median(values), statistics.mean(values) * 0.8])
            threshold = int(threshold)
            
            matching_respondents = find_respondents_with_numerical_rule(case_respondents, field, threshold, 'greater')
            
            question = template.format(field=field, threshold=threshold)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'filter_conditions': [{'field': field, 'threshold': threshold, 'comparison': 'greater'}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'numerical_rule',
                    'field': field,
                    'threshold': threshold,
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "numerical_between":
        field = random.choice(numerical_fields)
        
        # Get sample values to set reasonable range
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if values:
            min_val = int(min(values) + (max(values) - min(values)) * 0.2)
            max_val = int(min(values) + (max(values) - min(values)) * 0.8)
            
            matching_respondents = find_respondents_with_numerical_rule(case_respondents, field, (min_val, max_val), 'between')
            
            question = template.format(field=field, min_val=min_val, max_val=max_val)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'filter_conditions': [{'field': field, 'min_val': min_val, 'max_val': max_val, 'comparison': 'between'}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'numerical_range_rule',
                    'field': field,
                    'range': [min_val, max_val],
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # categorical_numerical
        # Get available categorical values
        cat_field = 'Gender'
        categories = list(set([r['answers'].get(cat_field) for r in case_respondents 
                              if r['answers'].get(cat_field) is not None]))
        
        if categories:
            cat_value = random.choice(categories)
            cat_text = decode_mcq_answer(cat_field, cat_value, questions_schema)
            
            field = random.choice(numerical_fields)
            
            # Get sample values to set threshold
            values = []
            for resp in case_respondents:
                val = resp['answers'].get(field)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass
            
            if values:
                threshold = int(statistics.median(values))
                
                matching_respondents = find_respondents_with_categorical_and_numerical_rule(
                    case_respondents, cat_field, cat_value, field, threshold, 'less'
                )
                
                question = template.format(category=cat_text.lower(), field=field, threshold=threshold)
                answer = [resp['respondent'] for resp in matching_respondents]
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': [cat_field, field],
                    'filter_conditions': [
                        {'field': cat_field, 'value': cat_value, 'decoded_value': cat_text},
                        {'field': field, 'threshold': threshold, 'comparison': 'less'}
                    ],
                    'reasoning_complexity': 2,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'categorical_numerical_rule',
                        'category': {'field': cat_field, 'value': cat_value, 'text': cat_text},
                        'numerical_field': field,
                        'threshold': threshold,
                        'comparison': 'less',
                        'matching_count': len(matching_respondents)
                    }
                }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("length_of_stay", "Find all respondents whose calculated length of stay is greater than {days} days."),
        ("multiple_conditions", "Which {category} respondents are over the age of {age} and have a '{field}' less than {threshold}?"),
        ("even_number_admission", "List all respondents whose '{field}' is an even number and who were admitted for an '{admission_type}' procedure.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "length_of_stay":
        # Calculate reasonable threshold based on case data
        los_values = []
        for resp in case_respondents:
            admission_date = resp['answers'].get('Date of Admission')
            discharge_date = resp['answers'].get('Discharge Date')
            if admission_date and discharge_date:
                los = calculate_length_of_stay(admission_date, discharge_date)
                if los is not None:
                    los_values.append(los)
        
        if los_values:
            days = int(statistics.median(los_values))
            
            matching_respondents = find_respondents_with_length_of_stay_rule(case_respondents, days, 'greater')
            
            question = template.format(days=days)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Date of Admission', 'Discharge Date'],
                'filter_conditions': [{'calculated_field': 'length_of_stay', 'threshold': days, 'comparison': 'greater'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'length_of_stay_rule',
                    'threshold_days': days,
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "multiple_conditions":
        # Get available genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                           if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema)
            
            # Get age values to set threshold
            ages = []
            for resp in case_respondents:
                age = resp['answers'].get('Age')
                if age is not None:
                    try:
                        ages.append(float(age))
                    except (ValueError, TypeError):
                        pass
            
            if ages:
                age_threshold = int(statistics.median(ages))
                field = 'Billing Amount'
                
                # Get billing values to set threshold
                billing_values = []
                for resp in case_respondents:
                    val = resp['answers'].get(field)
                    if val is not None:
                        try:
                            billing_values.append(float(val))
                        except (ValueError, TypeError):
                            pass
                
                if billing_values:
                    billing_threshold = int(statistics.median(billing_values))
                    
                    conditions = [
                        {'field': 'Gender', 'value': gender_code, 'comparison': 'equal'},
                        {'field': 'Age', 'threshold': age_threshold, 'comparison': 'greater'},
                        {'field': field, 'threshold': billing_threshold, 'comparison': 'less'}
                    ]
                    
                    matching_respondents = find_respondents_with_multiple_rules(case_respondents, conditions)
                    
                    question = template.format(
                        category=gender_text.lower(), age=age_threshold, field=field, threshold=billing_threshold
                    )
                    answer = [resp['respondent'] for resp in matching_respondents]
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': ['Gender', 'Age', field],
                        'filter_conditions': conditions,
                        'reasoning_complexity': 3,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'multiple_conditions',
                            'conditions': conditions,
                            'matching_count': len(matching_respondents)
                        }
                    }
    
    else:  # even_number_admission
        # Get available admission types
        admission_types = list(set([r['answers'].get('Admission Type') for r in case_respondents 
                                  if r['answers'].get('Admission Type') is not None]))
        
        if admission_types:
            admission_code = random.choice(admission_types)
            admission_text = decode_mcq_answer('Admission Type', admission_code, questions_schema)
            
            field = random.choice(['Age', 'Room Number'])
            
            conditions = [
                {'field': field, 'comparison': 'even'},
                {'field': 'Admission Type', 'value': admission_code, 'comparison': 'equal'}
            ]
            
            matching_respondents = find_respondents_with_multiple_rules(case_respondents, conditions)
            
            question = template.format(field=field, admission_type=admission_text.lower())
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [field, 'Admission Type'],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'even_number_admission_rule',
                    'even_field': field,
                    'admission_type': {'code': admission_code, 'text': admission_text},
                    'matching_count': len(matching_respondents)
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_group_average", "Find all respondents whose '{field}' is greater than the average '{field}' for their {group_field}."),
        ("los_multiple_group_avg", "Which respondents have a calculated length of stay that is more than double the average length of stay for their {group_field}?"),
        ("billing_above_condition_avg", "Which patients have a 'Billing Amount' that is higher than the average billing amount for all patients with the same medical condition?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_group_average":
        field = random.choice(['Age', 'Billing Amount'])
        group_field = random.choice(['Medical Condition', 'Insurance Provider'])
        
        matching_respondents = find_respondents_above_group_average(case_respondents, group_field, field)
        
        group_text = group_field.lower().replace(' ', ' ')
        
        question = template.format(field=field, group_field=group_text)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [group_field, field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_group_average',
                'group_field': group_field,
                'value_field': field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "los_multiple_group_avg":
        group_field = random.choice(['Admission Type', 'Medical Condition'])
        
        matching_respondents = find_respondents_with_los_multiple_of_group_average(case_respondents, group_field, 2.0)
        
        group_text = group_field.lower().replace(' ', ' ')
        
        question = template.format(group_field=group_text)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [group_field, 'Date of Admission', 'Discharge Date'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'los_multiple_group_average',
                'group_field': group_field,
                'multiplier': 2.0,
                'matching_count': len(matching_respondents)
            }
        }
    
    else:  # billing_above_condition_avg
        matching_respondents = find_respondents_above_group_average(case_respondents, 'Medical Condition', 'Billing Amount')
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Medical Condition', 'Billing Amount'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'billing_above_condition_average',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for healthcare rule-based querying using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/rule_based_querying/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_rule_based_qa.json"
    
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
            print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): {len(qa_pair['answer'])} respondents")
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
    answer_counts = []
    
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        respondent_counts.append(pair['case_respondent_count'])
        answer_counts.append(len(pair['answer']))
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n👥 Respondent counts per case:")
    print(f"  Average: {sum(respondent_counts)/len(respondent_counts):.1f} respondents per case")
    print(f"  Range: {min(respondent_counts)} - {max(respondent_counts)} respondents")
    
    print(f"\n🔢 Answer counts (matching respondents):")
    print(f"  Average: {sum(answer_counts)/len(answer_counts):.1f} respondents per question")
    print(f"  Range: {min(answer_counts)} - {max(answer_counts)} respondents")

if __name__ == "__main__":
    main()