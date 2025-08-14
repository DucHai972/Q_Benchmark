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
    
    # Parse options like "1. Male 2. Female"
    parts = mcq_part.strip().split()
    current_key = None
    current_value = []
    
    for part in parts:
        if part.endswith('.'):
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[:-1]  # Remove the dot
            current_value = []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(str(int(coded_answer)), str(coded_answer))

def extract_feature_values(respondents, features):
    """Extract all chosen features from respondents in this case only."""
    feature_values = {}
    
    for feature in features:
        feature_values[feature] = {}
        for resp in respondents:
            respondent_id = resp['respondent']
            # Handle nested features
            if '.' in feature:
                main_feature, sub_feature = feature.split('.', 1)
                value = resp['answers'].get(main_feature, {})
                if isinstance(value, dict):
                    raw_value = value.get(sub_feature)
                else:
                    raw_value = None
            else:
                raw_value = resp['answers'].get(feature)
            feature_values[feature][respondent_id] = raw_value
    
    return feature_values

def find_superlative_respondent(respondents, feature, mode='max', filters=None):
    """Find respondent with superlative value for a feature within this case."""
    filtered_respondents = respondents
    
    # Apply filters if provided
    if filters:
        for filter_feature, filter_value in filters.items():
            new_filtered = []
            for resp in filtered_respondents:
                if '.' in filter_feature:
                    main_feature, sub_feature = filter_feature.split('.', 1)
                    resp_value = resp['answers'].get(main_feature, {})
                    if isinstance(resp_value, dict):
                        resp_value = resp_value.get(sub_feature)
                    else:
                        resp_value = None
                else:
                    resp_value = resp['answers'].get(filter_feature)
                
                if resp_value == filter_value:
                    new_filtered.append(resp)
            filtered_respondents = new_filtered
    
    if not filtered_respondents:
        return None, None
        
    # Get numeric values for comparison
    valid_respondents = []
    for resp in filtered_respondents:
        if '.' in feature:
            main_feature, sub_feature = feature.split('.', 1)
            value = resp['answers'].get(main_feature, {})
            if isinstance(value, dict):
                value = value.get(sub_feature)
            else:
                value = None
        else:
            value = resp['answers'].get(feature)
            
        if value is not None:
            try:
                numeric_value = float(value)
                valid_respondents.append((resp, numeric_value))
            except (ValueError, TypeError):
                # For non-numeric, use original value
                valid_respondents.append((resp, value))
    
    if not valid_respondents:
        return None, None
    
    # Find superlative
    if mode == 'max':
        result = max(valid_respondents, key=lambda x: x[1])
    elif mode == 'min':
        result = min(valid_respondents, key=lambda x: x[1])
    else:
        result = valid_respondents[0]
    
    return result[0], result[1]

def calculate_group_statistics(respondents, feature, group_feature, group_value):
    """Calculate statistics for a feature within a specific group in this case."""
    group_respondents = []
    for resp in respondents:
        if '.' in group_feature:
            main_feature, sub_feature = group_feature.split('.', 1)
            resp_value = resp['answers'].get(main_feature, {})
            if isinstance(resp_value, dict):
                resp_value = resp_value.get(sub_feature)
            else:
                resp_value = None
        else:
            resp_value = resp['answers'].get(group_feature)
        
        if resp_value == group_value:
            group_respondents.append(resp)
    
    values = []
    for resp in group_respondents:
        if '.' in feature:
            main_feature, sub_feature = feature.split('.', 1)
            value = resp['answers'].get(main_feature, {})
            if isinstance(value, dict):
                value = value.get(sub_feature)
            else:
                value = None
        else:
            value = resp['answers'].get(feature)
            
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    if not values:
        return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
    
    return {
        'count': len(values),
        'average': statistics.mean(values),
        'min': min(values),
        'max': max(values)
    }

def generate_student_name():
    """Generate a random student name with varied case formatting."""
    first_names = ['Alex', 'Sam', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Avery', 
                   'Quinn', 'Cameron', 'Blake', 'Drew', 'Sage', 'Rowan', 'Parker', 'Emery']
    last_names = ['Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 
                  'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia']
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    case_styles = [
        lambda s: s.upper(),           # ALEX JOHNSON
        lambda s: s.lower(),           # alex johnson  
        lambda s: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)), # AlEx JoHnSoN
        lambda s: s                    # Alex Johnson (normal)
    ]
    
    style = random.choice(case_styles)
    return f"{style(first)} {style(last)}"

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Basic demographic features
    basic_features = ['Year of birth', 'Gender', 'Socio-economic status', 'Ethnic identity', 
                     'Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                     'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    # Nested features
    nested_features = [f for f in features if '.' in f]
    
    templates = [
        ("direct_respondent", "What is the {feature} of respondent '{respondent_id}'?"),
        ("demographic_filter", "What is the {feature} of the respondent with {filter_feature} = {filter_value}?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    selected_features = [target_feature]
    
    if template_type == "direct_respondent":
        # Pick a random respondent from this case
        respondent = random.choice(case_respondents)
        question = template.format(feature=target_feature, respondent_id=respondent['respondent'])
        
        # Get the answer
        if '.' in target_feature:
            main_feature, sub_feature = target_feature.split('.', 1)
            value = respondent['answers'].get(main_feature, {})
            if isinstance(value, dict):
                answer = str(value.get(sub_feature, 'N/A'))
            else:
                answer = 'N/A'
        else:
            answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
        
        feature_values = extract_feature_values(case_respondents, selected_features)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': selected_features,
            'target_respondent': respondent['respondent'],
            'student_name': 'N/A',
            'reasoning_complexity': 1,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'direct_lookup',
                'target_value': respondent['answers'].get(target_feature.split('.')[0] if '.' in target_feature else target_feature)
            }
        }
        
    else:  # demographic_filter
        # Find respondent with specific demographic characteristic
        filter_features = [f for f in basic_features if f != target_feature and f in [r['answers'].keys() for r in case_respondents][0]]
        if filter_features:
            filter_feature = random.choice(filter_features)
            
            # Find possible values for the filter within this case
            possible_values = list(set([r['answers'].get(filter_feature) for r in case_respondents 
                                      if r['answers'].get(filter_feature) is not None]))
            
            if possible_values:
                filter_value = random.choice(possible_values)
                selected_features = [target_feature, filter_feature]
                
                # Find respondent matching filter
                matching_respondents = [r for r in case_respondents 
                                      if r['answers'].get(filter_feature) == filter_value]
                
                if matching_respondents:
                    respondent = random.choice(matching_respondents)
                    decoded_filter_value = decode_mcq_answer(filter_feature, filter_value, questions_schema)
                    
                    question = template.format(feature=target_feature, filter_feature=filter_feature, 
                                             filter_value=decoded_filter_value)
                    
                    if '.' in target_feature:
                        main_feature, sub_feature = target_feature.split('.', 1)
                        value = respondent['answers'].get(main_feature, {})
                        if isinstance(value, dict):
                            answer = str(value.get(sub_feature, 'N/A'))
                        else:
                            answer = 'N/A'
                    else:
                        answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Easy",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'student_name': 'N/A',
                        'reasoning_complexity': 2,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'demographic_filter',
                            'filter_conditions': {
                                filter_feature: {'raw': filter_value, 'decoded': decoded_filter_value}
                            }
                        }
                    }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    # Score-based features for finding superlatives
    score_features = [f for f in features if ('Frequency' in f or 'satisfaction' in f or 
                     f in ['Happiness', 'Laughter', 'Learning', 'Enjoyment', 'Worry', 
                          'Depression', 'Anger', 'Stress', 'Loneliness'])]
    
    templates = [
        ("highest_in_group", "What is the {feature} of the respondent with the highest {score_feature} among those with {group_feature} = {group_value}?"),
        ("score_combination", "What is the {feature} of the respondent whose {score_a} was {value_a} and {score_b} was {value_b}?"),
        ("score_total", "What is the {feature} of the respondent whose total score for {score_a} and {score_b} was exactly {total}?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    
    if template_type == "highest_in_group":
        # Find highest score within a specific demographic group within this case
        score_feature = random.choice(score_features)
        group_features = ['Gender', 'Socio-economic status', 'Ethnic identity']
        
        if group_features:
            group_feature = random.choice(group_features)
            selected_features = [target_feature, score_feature, group_feature]
            
            # Find possible group values within this case
            possible_groups = list(set([r['answers'].get(group_feature) for r in case_respondents 
                                      if r['answers'].get(group_feature) is not None]))
            
            if possible_groups:
                group_value = random.choice(possible_groups)
                
                # Find highest score in this group within this case
                filters = {group_feature: group_value}
                respondent, score_value = find_superlative_respondent(case_respondents, score_feature, 'max', filters)
                
                if respondent:
                    decoded_group_value = decode_mcq_answer(group_feature, group_value, questions_schema)
                    
                    question = template.format(feature=target_feature, score_feature=score_feature, 
                                             group_feature=group_feature, group_value=decoded_group_value)
                    
                    if '.' in target_feature:
                        main_feature, sub_feature = target_feature.split('.', 1)
                        value = respondent['answers'].get(main_feature, {})
                        if isinstance(value, dict):
                            answer = str(value.get(sub_feature, 'N/A'))
                        else:
                            answer = 'N/A'
                    else:
                        answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    group_stats = calculate_group_statistics(case_respondents, score_feature, group_feature, group_value)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'student_name': 'N/A',
                        'reasoning_complexity': 3,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'group_superlative',
                            'score_feature': score_feature,
                            'group_feature': group_feature,
                            'group_value': {'raw': group_value, 'decoded': decoded_group_value},
                            'superlative_value': score_value,
                            'group_statistics': group_stats
                        }
                    }
    
    elif template_type == "score_combination":
        # Find respondent with specific score combination within this case
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            selected_features = [target_feature, score_a, score_b]
            
            # Find a respondent with valid scores for both features within this case
            valid_respondents = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_a.split('.')[0] if '.' in score_a else score_a)
                val_b = resp['answers'].get(score_b.split('.')[0] if '.' in score_b else score_b)
                
                if '.' in score_a and isinstance(val_a, dict):
                    val_a = val_a.get(score_a.split('.')[1])
                if '.' in score_b and isinstance(val_b, dict):
                    val_b = val_b.get(score_b.split('.')[1])
                
                if val_a is not None and val_b is not None:
                    valid_respondents.append(resp)
            
            if valid_respondents:
                respondent = random.choice(valid_respondents)
                val_a = respondent['answers'].get(score_a.split('.')[0] if '.' in score_a else score_a)
                val_b = respondent['answers'].get(score_b.split('.')[0] if '.' in score_b else score_b)
                
                if '.' in score_a and isinstance(val_a, dict):
                    val_a = val_a.get(score_a.split('.')[1])
                if '.' in score_b and isinstance(val_b, dict):
                    val_b = val_b.get(score_b.split('.')[1])
                
                question = template.format(feature=target_feature, score_a=score_a, 
                                         value_a=val_a, score_b=score_b, value_b=val_b)
                
                if '.' in target_feature:
                    main_feature, sub_feature = target_feature.split('.', 1)
                    value = respondent['answers'].get(main_feature, {})
                    if isinstance(value, dict):
                        answer = str(value.get(sub_feature, 'N/A'))
                    else:
                        answer = 'N/A'
                else:
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'student_name': 'N/A',
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'score_combination_filter',
                        'filter_conditions': {
                            score_a: val_a,
                            score_b: val_b
                        }
                    }
                }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    # Focus on mental health score features
    mental_health_features = [f for f in features if ('Frequency' in f and 
                             ('Anxiety' in f or 'Depression' in f or 'Emotional' in f))]
    
    template = "What is the {feature} of the respondent whose {score_feature} is higher than the average {score_feature} for all respondents with {group_feature} = {group_value} in this case?"
    
    target_feature = random.choice(features)
    
    if mental_health_features:
        score_feature = random.choice(mental_health_features)
        group_features = ['Gender', 'Socio-economic status']
        
        if group_features:
            group_feature = random.choice(group_features)
            selected_features = [target_feature, score_feature, group_feature]
            
            # Get possible group values within this case
            possible_groups = list(set([r['answers'].get(group_feature) for r in case_respondents 
                                      if r['answers'].get(group_feature) is not None]))
            
            if possible_groups:
                group_value = random.choice(possible_groups)
                
                # Calculate average score for this group within this case
                group_stats = calculate_group_statistics(case_respondents, score_feature, group_feature, group_value)
                group_avg = group_stats['average']
                
                # Find respondents in this group whose score is above average within this case
                above_avg_respondents = []
                for resp in case_respondents:
                    resp_group_val = resp['answers'].get(group_feature)
                    if resp_group_val == group_value:
                        if '.' in score_feature:
                            main_feature, sub_feature = score_feature.split('.', 1)
                            score_val = resp['answers'].get(main_feature, {})
                            if isinstance(score_val, dict):
                                score_val = score_val.get(sub_feature)
                            else:
                                score_val = None
                        else:
                            score_val = resp['answers'].get(score_feature)
                        
                        if score_val is not None:
                            try:
                                if float(score_val) > group_avg:
                                    above_avg_respondents.append((resp, float(score_val)))
                            except (ValueError, TypeError):
                                pass
                
                if above_avg_respondents:
                    # Pick one of the above-average respondents
                    respondent, score_value = random.choice(above_avg_respondents)
                    decoded_group_value = decode_mcq_answer(group_feature, group_value, questions_schema)
                    
                    question = template.format(
                        feature=target_feature, score_feature=score_feature,
                        group_feature=group_feature, group_value=decoded_group_value
                    )
                    
                    if '.' in target_feature:
                        main_feature, sub_feature = target_feature.split('.', 1)
                        value = respondent['answers'].get(main_feature, {})
                        if isinstance(value, dict):
                            answer = str(value.get(sub_feature, 'N/A'))
                        else:
                            answer = 'N/A'
                    else:
                        answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Really Hard",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'student_name': 'N/A',
                        'reasoning_complexity': 5,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'above_average_in_group_within_case',
                            'score_feature': score_feature,
                            'group_feature': group_feature,
                            'group_value': {'raw': group_value, 'decoded': decoded_group_value},
                            'group_average': group_avg,
                            'respondent_score': score_value,
                            'above_average_candidates': len(above_avg_respondents),
                            'group_statistics': group_stats
                        }
                    }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health answer lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/self-reported-mental-health_answer_lookup_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names including nested ones
    features = []
    for key in sample_data['questions'].keys():
        if key != 'respondent':
            if isinstance(sample_data['questions'][key], dict) and 'sub_questions' in sample_data['questions'][key]:
                # Handle nested features
                for sub_key in sample_data['questions'][key]['sub_questions'].keys():
                    features.append(f"{key}.{sub_key}")
            else:
                features.append(key)
    
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
        
        print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): Features: {qa_pair['selected_features']} -> '{qa_pair['answer']}'")
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs using case-specific data")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    difficulty_counts = {}
    respondent_counts = []
    
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        respondent_counts.append(pair['case_respondent_count'])
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n👥 Respondent counts per case:")
    print(f"  Average: {sum(respondent_counts)/len(respondent_counts):.1f} respondents per case")
    print(f"  Range: {min(respondent_counts)} - {max(respondent_counts)} respondents")

if __name__ == "__main__":
    main()