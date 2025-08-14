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
    """Calculate length of stay in days between admission and discharge dates."""
    try:
        admit_dt = datetime.strptime(admission_date, '%Y-%m-%d')
        discharge_dt = datetime.strptime(discharge_date, '%Y-%m-%d')
        return (discharge_dt - admit_dt).days
    except (ValueError, TypeError):
        return None

def count_respondents_with_categorical_filter(respondents, field, value):
    """Count respondents with specific categorical field value."""
    count = 0
    for resp in respondents:
        if resp['answers'].get(field) == value:
            count += 1
    return count

def count_respondents_with_numerical_filter(respondents, field, threshold, comparison='greater'):
    """Count respondents with numerical field meeting threshold condition."""
    count = 0
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                value_num = float(value)
                if comparison == 'greater' and value_num > threshold:
                    count += 1
                elif comparison == 'less' and value_num < threshold:
                    count += 1
                elif comparison == 'equal' and value_num == threshold:
                    count += 1
                elif comparison == 'between' and isinstance(threshold, tuple):
                    min_val, max_val = threshold
                    if min_val <= value_num <= max_val:
                        count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_multiple_conditions(respondents, conditions):
    """Count respondents meeting multiple conditions."""
    count = 0
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in conditions:
            field = condition['field']
            value = condition['value']
            comparison = condition.get('comparison', 'equal')
            
            resp_value = resp['answers'].get(field)
            if resp_value is None:
                meets_all_conditions = False
                break
            
            if comparison == 'equal':
                if resp_value != value:
                    meets_all_conditions = False
                    break
            elif comparison == 'greater':
                try:
                    if float(resp_value) <= value:
                        meets_all_conditions = False
                        break
                except (ValueError, TypeError):
                    meets_all_conditions = False
                    break
            elif comparison == 'less':
                try:
                    if float(resp_value) >= value:
                        meets_all_conditions = False
                        break
                except (ValueError, TypeError):
                    meets_all_conditions = False
                    break
        
        if meets_all_conditions:
            count += 1
    
    return count

def count_respondents_with_length_of_stay_filter(respondents, min_days, max_days):
    """Count respondents with length of stay between min and max days."""
    count = 0
    for resp in respondents:
        admission = resp['answers'].get('Date of Admission')
        discharge = resp['answers'].get('Discharge Date')
        if admission and discharge:
            los = calculate_length_of_stay(admission, discharge)
            if los is not None and min_days <= los <= max_days:
                count += 1
    return count

def calculate_average_for_group(respondents, group_field, group_value, target_field):
    """Calculate average of target field for respondents in specific group."""
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

def count_respondents_above_group_average(respondents, group_field, target_field):
    """Count respondents with target field above their group's average."""
    count = 0
    
    # Get unique group values
    groups = list(set([r['answers'].get(group_field) for r in respondents 
                      if r['answers'].get(group_field) is not None]))
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_value = resp['answers'].get(target_field)
        
        if resp_group and resp_value is not None:
            try:
                resp_value_num = float(resp_value)
                group_avg = calculate_average_for_group(respondents, group_field, resp_group, target_field)
                
                if resp_value_num > group_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Categorical and numerical fields for easy counting
    categorical_fields = ['Gender', 'Blood Type', 'Medical Condition', 'Insurance Provider', 'Admission Type', 'Medication', 'Test Results']
    numerical_fields = ['Age', 'Billing Amount']
    
    templates = [
        ("categorical_single", "Count the respondents with a '{field}' of '{value}'."),
        ("numerical_threshold", "Count the respondents whose '{field}' is {comparison} than {threshold}."),
        ("two_conditions", "Count the respondents with '{field_a}' = '{value_a}' and '{field_b}' = '{value_b}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "categorical_single":
        field = random.choice(categorical_fields)
        
        # Get available values for this field
        available_values = list(set([r['answers'].get(field) for r in case_respondents 
                                   if r['answers'].get(field) is not None]))
        
        if available_values:
            value = random.choice(available_values)
            decoded_value = decode_mcq_answer(field, value, questions_schema)
            
            count = count_respondents_with_categorical_filter(case_respondents, field, value)
            
            question = template.format(field=field, value=decoded_value)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'filter_conditions': [{'field': field, 'value': value, 'decoded_value': decoded_value}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'categorical_single_filter',
                    'field': field,
                    'filter_value': {'raw': value, 'decoded': decoded_value},
                    'matching_count': count
                }
            }
    
    elif template_type == "numerical_threshold":
        field = random.choice(numerical_fields)
        comparison_type = random.choice(['greater', 'less'])
        
        if field == 'Age':
            threshold = random.choice([30, 40, 50, 60, 70, 80])
        else:  # Billing Amount
            threshold = random.choice([15000, 20000, 25000, 30000, 40000])
        
        comparison_text = "greater" if comparison_type == "greater" else "less"
        
        count = count_respondents_with_numerical_filter(case_respondents, field, threshold, comparison_type)
        
        question = template.format(field=field, comparison=comparison_text, threshold=threshold)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [field],
            'filter_conditions': [{'field': field, 'threshold': threshold, 'comparison': comparison_type}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'numerical_threshold_filter',
                'field': field,
                'threshold': threshold,
                'comparison': comparison_type,
                'matching_count': count
            }
        }
    
    else:  # two_conditions
        field_a = random.choice(categorical_fields)
        field_b = random.choice([f for f in categorical_fields if f != field_a])
        
        # Get available values
        values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                           if r['answers'].get(field_a) is not None]))
        values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                           if r['answers'].get(field_b) is not None]))
        
        if values_a and values_b:
            value_a = random.choice(values_a)
            value_b = random.choice(values_b)
            
            decoded_a = decode_mcq_answer(field_a, value_a, questions_schema)
            decoded_b = decode_mcq_answer(field_b, value_b, questions_schema)
            
            conditions = [
                {'field': field_a, 'value': value_a, 'comparison': 'equal'},
                {'field': field_b, 'value': value_b, 'comparison': 'equal'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(field_a=field_a, value_a=decoded_a, field_b=field_b, value_b=decoded_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field_a, field_b],
                'filter_conditions': [
                    {'field': field_a, 'value': value_a, 'decoded_value': decoded_a},
                    {'field': field_b, 'value': value_b, 'decoded_value': decoded_b}
                ],
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'multiple_categorical_conditions',
                    'conditions': conditions,
                    'matching_count': count
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    categorical_fields = ['Gender', 'Blood Type', 'Medical Condition', 'Insurance Provider', 'Admission Type', 'Medication', 'Test Results']
    
    templates = [
        ("three_conditions", "Count the respondents with '{field_a}' = '{value_a}' and '{field_b}' = '{value_b}' who have a '{numerical_field}' {comparison} {threshold}."),
        ("length_of_stay", "Count the respondents whose calculated length of stay is between {min_days} and {max_days} days and who have '{condition_field}' = '{condition_value}'."),
        ("hospital_billing_combo", "Count the respondents from '{hospital}' with '{medical_condition}' who have a billing amount greater than {billing_threshold}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "three_conditions":
        field_a = random.choice(categorical_fields)
        field_b = random.choice([f for f in categorical_fields if f != field_a])
        numerical_field = random.choice(['Age', 'Billing Amount'])
        comparison_type = random.choice(['greater', 'less'])
        
        # Get available values
        values_a = list(set([r['answers'].get(field_a) for r in case_respondents 
                           if r['answers'].get(field_a) is not None]))
        values_b = list(set([r['answers'].get(field_b) for r in case_respondents 
                           if r['answers'].get(field_b) is not None]))
        
        if values_a and values_b:
            value_a = random.choice(values_a)
            value_b = random.choice(values_b)
            
            if numerical_field == 'Age':
                threshold = random.choice([50, 60, 70])
            else:
                threshold = random.choice([20000, 25000, 30000])
            
            decoded_a = decode_mcq_answer(field_a, value_a, questions_schema)
            decoded_b = decode_mcq_answer(field_b, value_b, questions_schema)
            
            conditions = [
                {'field': field_a, 'value': value_a, 'comparison': 'equal'},
                {'field': field_b, 'value': value_b, 'comparison': 'equal'},
                {'field': numerical_field, 'value': threshold, 'comparison': comparison_type}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            comparison_text = "greater" if comparison_type == "greater" else "less"
            question = template.format(
                field_a=field_a, value_a=decoded_a, field_b=field_b, value_b=decoded_b,
                numerical_field=numerical_field, comparison=comparison_text, threshold=threshold
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [field_a, field_b, numerical_field],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'three_condition_filter',
                    'conditions': conditions,
                    'matching_count': count
                }
            }
    
    elif template_type == "length_of_stay":
        min_days = random.choice([5, 7, 10])
        max_days = min_days + random.choice([5, 10, 15])
        
        condition_field = random.choice(categorical_fields)
        available_values = list(set([r['answers'].get(condition_field) for r in case_respondents 
                                   if r['answers'].get(condition_field) is not None]))
        
        if available_values:
            condition_value = random.choice(available_values)
            decoded_condition = decode_mcq_answer(condition_field, condition_value, questions_schema)
            
            # Count respondents meeting both length of stay and condition
            count = 0
            for resp in case_respondents:
                admission = resp['answers'].get('Date of Admission')
                discharge = resp['answers'].get('Discharge Date')
                field_value = resp['answers'].get(condition_field)
                
                if admission and discharge and field_value == condition_value:
                    los = calculate_length_of_stay(admission, discharge)
                    if los is not None and min_days <= los <= max_days:
                        count += 1
            
            question = template.format(
                min_days=min_days, max_days=max_days, 
                condition_field=condition_field, condition_value=decoded_condition
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Date of Admission', 'Discharge Date', condition_field],
                'filter_conditions': [
                    {'field': 'length_of_stay', 'min_days': min_days, 'max_days': max_days},
                    {'field': condition_field, 'value': condition_value, 'decoded_value': decoded_condition}
                ],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'length_of_stay_plus_condition',
                    'length_of_stay_range': [min_days, max_days],
                    'condition': {'field': condition_field, 'value': condition_value},
                    'matching_count': count
                }
            }
    
    else:  # hospital_billing_combo
        # Get available hospitals and medical conditions
        hospitals = list(set([r['answers'].get('Hospital') for r in case_respondents 
                            if r['answers'].get('Hospital') is not None]))
        conditions = list(set([r['answers'].get('Medical Condition') for r in case_respondents 
                             if r['answers'].get('Medical Condition') is not None]))
        
        if hospitals and conditions:
            hospital = random.choice(hospitals)
            medical_condition = random.choice(conditions)
            billing_threshold = random.choice([15000, 20000, 25000, 30000])
            
            decoded_condition = decode_mcq_answer('Medical Condition', medical_condition, questions_schema)
            
            filter_conditions = [
                {'field': 'Hospital', 'value': hospital, 'comparison': 'equal'},
                {'field': 'Medical Condition', 'value': medical_condition, 'comparison': 'equal'},
                {'field': 'Billing Amount', 'value': billing_threshold, 'comparison': 'greater'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, filter_conditions)
            
            question = template.format(
                hospital=hospital, medical_condition=decoded_condition, billing_threshold=billing_threshold
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Hospital', 'Medical Condition', 'Billing Amount'],
                'filter_conditions': filter_conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'hospital_condition_billing_filter',
                    'conditions': filter_conditions,
                    'matching_count': count
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    numerical_fields = ['Age', 'Billing Amount']
    grouping_fields = ['Medical Condition', 'Insurance Provider', 'Hospital']
    
    templates = [
        ("above_group_average", "Count the respondents with a '{numerical_field}' that is higher than the average '{numerical_field}' for their '{grouping_field}'."),
        ("overall_average_comparison", "Count the respondents with '{condition}' who have a '{numerical_field}' that is lower than the overall average for all respondents."),
        ("group_size_comparison", "Count the respondents who are in a '{grouping_field}' where the number of individuals with '{condition_a}' is greater than the number with '{condition_b}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_group_average":
        numerical_field = random.choice(numerical_fields)
        grouping_field = random.choice(grouping_fields)
        
        count = count_respondents_above_group_average(case_respondents, grouping_field, numerical_field)
        
        question = template.format(numerical_field=numerical_field, grouping_field=grouping_field)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [numerical_field, grouping_field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_group_average',
                'numerical_field': numerical_field,
                'grouping_field': grouping_field,
                'matching_count': count
            }
        }
    
    elif template_type == "overall_average_comparison":
        numerical_field = random.choice(numerical_fields)
        condition_field = random.choice(['Medical Condition', 'Insurance Provider'])
        
        # Get available condition values
        available_conditions = list(set([r['answers'].get(condition_field) for r in case_respondents 
                                       if r['answers'].get(condition_field) is not None]))
        
        if available_conditions:
            condition_value = random.choice(available_conditions)
            decoded_condition = decode_mcq_answer(condition_field, condition_value, questions_schema)
            
            # Calculate overall average
            all_values = []
            for resp in case_respondents:
                value = resp['answers'].get(numerical_field)
                if value is not None:
                    try:
                        all_values.append(float(value))
                    except (ValueError, TypeError):
                        pass
            
            if all_values:
                overall_avg = statistics.mean(all_values)
                
                # Count respondents with condition and below overall average
                count = 0
                for resp in case_respondents:
                    if resp['answers'].get(condition_field) == condition_value:
                        value = resp['answers'].get(numerical_field)
                        if value is not None:
                            try:
                                if float(value) < overall_avg:
                                    count += 1
                            except (ValueError, TypeError):
                                pass
                
                question = template.format(
                    condition=f"{condition_field} = '{decoded_condition}'",
                    numerical_field=numerical_field
                )
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': [condition_field, numerical_field],
                    'filter_conditions': [{'field': condition_field, 'value': condition_value, 'decoded_value': decoded_condition}],
                    'reasoning_complexity': 5,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'condition_below_overall_average',
                        'condition_field': condition_field,
                        'condition_value': condition_value,
                        'numerical_field': numerical_field,
                        'overall_average': overall_avg,
                        'matching_count': count
                    }
                }
    
    elif template_type == "group_size_comparison":
        grouping_field = random.choice(grouping_fields)
        condition_field = 'Medical Condition'  # Use medical condition for comparison
        
        # Get available conditions
        available_conditions = list(set([r['answers'].get(condition_field) for r in case_respondents 
                                       if r['answers'].get(condition_field) is not None]))
        
        if len(available_conditions) >= 2:
            condition_a, condition_b = random.sample(available_conditions, 2)
            decoded_a = decode_mcq_answer(condition_field, condition_a, questions_schema)
            decoded_b = decode_mcq_answer(condition_field, condition_b, questions_schema)
            
            # Get unique groups
            groups = list(set([r['answers'].get(grouping_field) for r in case_respondents 
                             if r['answers'].get(grouping_field) is not None]))
            
            qualifying_groups = []
            for group in groups:
                group_respondents = [r for r in case_respondents if r['answers'].get(grouping_field) == group]
                
                count_a = sum(1 for r in group_respondents if r['answers'].get(condition_field) == condition_a)
                count_b = sum(1 for r in group_respondents if r['answers'].get(condition_field) == condition_b)
                
                if count_a > count_b:
                    qualifying_groups.append(group)
            
            # Count all respondents in qualifying groups
            count = sum(1 for r in case_respondents if r['answers'].get(grouping_field) in qualifying_groups)
            
            question = template.format(
                grouping_field=grouping_field,
                condition_a=f"{condition_field} = '{decoded_a}'",
                condition_b=f"{condition_field} = '{decoded_b}'"
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': [grouping_field, condition_field],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_size_comparison',
                    'grouping_field': grouping_field,
                    'condition_a': condition_a,
                    'condition_b': condition_b,
                    'qualifying_groups': qualifying_groups,
                    'matching_count': count
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare respondent count using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/respondent_count/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_respondent_count_qa.json"
    
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
            print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): {qa_pair['answer']} respondents")
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
        answer_counts.append(int(pair['answer']))
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n👥 Respondent counts per case:")
    print(f"  Average: {sum(respondent_counts)/len(respondent_counts):.1f} respondents per case")
    print(f"  Range: {min(respondent_counts)} - {max(respondent_counts)} respondents")
    
    print(f"\n🔢 Answer counts (respondents meeting criteria):")
    print(f"  Average: {sum(answer_counts)/len(answer_counts):.1f} respondents per question")
    print(f"  Range: {min(answer_counts)} - {max(answer_counts)} respondents")

if __name__ == "__main__":
    main()