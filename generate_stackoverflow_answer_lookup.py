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
    
    return options.get(str(coded_answer), str(coded_answer))

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

def find_superlative_respondent(respondents, feature, mode='max', filters=None):
    """Find respondent with superlative value for a feature within this case."""
    filtered_respondents = respondents
    
    # Apply filters if provided
    if filters:
        for filter_feature, filter_value in filters.items():
            filtered_respondents = [r for r in filtered_respondents 
                                  if r['answers'].get(filter_feature) == filter_value]
    
    if not filtered_respondents:
        return None, None
        
    # Get numeric values for comparison
    valid_respondents = []
    for resp in filtered_respondents:
        value = resp['answers'].get(feature)
        if value is not None:
            try:
                # Handle numeric fields like YearsCode, YearsCodePro, CompTotal
                numeric_value = float(value)
                valid_respondents.append((resp, numeric_value))
            except (ValueError, TypeError):
                # Skip non-numeric values for numeric comparison
                pass
    
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
    group_respondents = [r for r in respondents 
                        if r['answers'].get(group_feature) == group_value]
    
    values = []
    for resp in group_respondents:
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

def generate_developer_name():
    """Generate a random developer name with varied case formatting."""
    first_names = ['Alex', 'Sam', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Avery', 
                   'Quinn', 'Cameron', 'Blake', 'Drew', 'Sage', 'Robin', 'Parker', 'Jamie']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Taylor']
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    case_styles = [
        lambda s: s.upper(),           # ALEX SMITH
        lambda s: s.lower(),           # alex smith  
        lambda s: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)), # AlEx SmItH
        lambda s: s                    # Alex Smith (normal)
    ]
    
    style = random.choice(case_styles)
    return f"{style(first)} {style(last)}"

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Numeric features for superlative questions
    numeric_features = ['YearsCode', 'YearsCodePro', 'CompTotal']
    
    # Categorical features for filtering
    categorical_features = ['MainBranch', 'Employment', 'EdLevel', 'Country', 'CompFreq', 'VersionControlSystem']
    
    templates = [
        ("direct_respondent", "What is the {feature} of respondent '{respondent_id}'?"),
        ("superlative", "What is the {feature} of the respondent with the {superlative} {numeric_feature}?"),
        ("category_filter", "What is the {feature} of the respondent with {filter_feature} = '{filter_value}'?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    selected_features = [target_feature]
    
    if template_type == "direct_respondent":
        # Pick a random respondent from this case
        respondent = random.choice(case_respondents)
        question = template.format(feature=target_feature, respondent_id=respondent['respondent'])
        answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
        
        feature_values = extract_feature_values(case_respondents, selected_features)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': selected_features,
            'target_respondent': respondent['respondent'],
            'developer_name': 'N/A',
            'reasoning_complexity': 1,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'direct_lookup',
                'target_value': respondent['answers'][target_feature]
            }
        }
        
    elif template_type == "superlative":
        # Find developer with highest/lowest experience, compensation, etc. within this case
        if numeric_features:
            numeric_feature = random.choice(numeric_features)
            superlative = random.choice(['highest', 'lowest'])
            mode = 'max' if superlative == 'highest' else 'min'
            
            selected_features = [target_feature, numeric_feature]
            respondent, superlative_value = find_superlative_respondent(case_respondents, numeric_feature, mode)
            
            if respondent:
                question = template.format(feature=target_feature, superlative=superlative, 
                                         numeric_feature=numeric_feature)
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'developer_name': 'N/A',
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'superlative',
                        'superlative_type': mode,
                        'superlative_feature': numeric_feature,
                        'superlative_value': superlative_value
                    }
                }
        
        # Fallback to direct respondent
        return generate_easy_question(case_id, case_respondents, features, questions_schema)
    
    else:  # category_filter
        # Find respondent with specific category within this case
        if categorical_features:
            filter_feature = random.choice([f for f in categorical_features if f != target_feature])
            selected_features = [target_feature, filter_feature]
            
            # Find possible values for the filter within this case
            possible_values = list(set([r['answers'].get(filter_feature) for r in case_respondents 
                                      if r['answers'].get(filter_feature) is not None]))
            
            if possible_values:
                filter_value = random.choice(possible_values)
                
                # Find respondent matching filter
                matching_respondents = [r for r in case_respondents 
                                      if r['answers'].get(filter_feature) == filter_value]
                
                if matching_respondents:
                    respondent = random.choice(matching_respondents)
                    decoded_filter_value = decode_mcq_answer(filter_feature, filter_value, questions_schema)
                    
                    question = template.format(feature=target_feature, filter_feature=filter_feature, 
                                             filter_value=decoded_filter_value)
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Easy",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'developer_name': 'N/A',
                        'reasoning_complexity': 2,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'category_filter',
                            'filter_conditions': {
                                filter_feature: {'raw': filter_value, 'decoded': decoded_filter_value}
                            }
                        }
                    }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    numeric_features = ['YearsCode', 'YearsCodePro', 'CompTotal']
    categorical_features = ['MainBranch', 'Employment', 'EdLevel', 'Country', 'CompFreq']
    
    templates = [
        ("superlative_in_group", "What is the {feature} of the respondent with the {superlative} {numeric_feature} among those with {group_feature} = '{group_value}'?"),
        ("multi_condition", "What is the {feature} of the respondent with {field_a} = '{value_a}' and {field_b} = '{value_b}'?"),
        ("experience_total", "What is the {feature} of the respondent whose total years of coding experience (YearsCode + YearsCodePro) was exactly {total}?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    
    if template_type == "superlative_in_group":
        # Find superlative within a specific group within this case
        if numeric_features and categorical_features:
            numeric_feature = random.choice(numeric_features)
            group_feature = random.choice([f for f in categorical_features if f != target_feature])
            selected_features = [target_feature, numeric_feature, group_feature]
            
            # Find possible group values within this case
            possible_groups = list(set([r['answers'].get(group_feature) for r in case_respondents 
                                      if r['answers'].get(group_feature) is not None]))
            
            if possible_groups:
                group_value = random.choice(possible_groups)
                superlative = random.choice(['highest', 'lowest'])
                mode = 'max' if superlative == 'highest' else 'min'
                
                # Find superlative in this group within this case
                filters = {group_feature: group_value}
                respondent, superlative_value = find_superlative_respondent(case_respondents, numeric_feature, mode, filters)
                
                if respondent:
                    decoded_group_value = decode_mcq_answer(group_feature, group_value, questions_schema)
                    
                    question = template.format(feature=target_feature, superlative=superlative, 
                                             numeric_feature=numeric_feature, group_feature=group_feature, 
                                             group_value=decoded_group_value)
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    group_stats = calculate_group_statistics(case_respondents, numeric_feature, group_feature, group_value)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'developer_name': 'N/A',
                        'reasoning_complexity': 3,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'group_superlative',
                            'numeric_feature': numeric_feature,
                            'superlative_type': mode,
                            'superlative_value': superlative_value,
                            'group_feature': group_feature,
                            'group_value': {'raw': group_value, 'decoded': decoded_group_value},
                            'group_statistics': group_stats
                        }
                    }
    
    elif template_type == "multi_condition":
        # Find respondent with multiple specific conditions within this case
        filter_features = [f for f in categorical_features if f != target_feature]
        if len(filter_features) >= 2:
            field_a, field_b = random.sample(filter_features, 2)
            selected_features = [target_feature, field_a, field_b]
            
            # Find a respondent that has values for both filters within this case
            valid_respondents = [r for r in case_respondents 
                               if r['answers'].get(field_a) and r['answers'].get(field_b)]
            if valid_respondents:
                respondent = random.choice(valid_respondents)
                value_a = respondent['answers'][field_a]
                value_b = respondent['answers'][field_b]
                
                decoded_value_a = decode_mcq_answer(field_a, value_a, questions_schema)
                decoded_value_b = decode_mcq_answer(field_b, value_b, questions_schema)
                
                question = template.format(feature=target_feature, field_a=field_a, 
                                         value_a=decoded_value_a, field_b=field_b, value_b=decoded_value_b)
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'developer_name': 'N/A',
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'multi_condition_filter',
                        'filter_conditions': {
                            field_a: {'raw': value_a, 'decoded': decoded_value_a},
                            field_b: {'raw': value_b, 'decoded': decoded_value_b}
                        }
                    }
                }
    
    elif template_type == "experience_total":
        # Find respondent with specific total experience within this case
        selected_features = [target_feature, 'YearsCode', 'YearsCodePro']
        
        # Calculate totals for all respondents in this case
        valid_respondents = []
        for resp in case_respondents:
            years_code = resp['answers'].get('YearsCode')
            years_code_pro = resp['answers'].get('YearsCodePro')
            if years_code and years_code_pro:
                try:
                    total = float(years_code) + float(years_code_pro)
                    valid_respondents.append((resp, total))
                except (ValueError, TypeError):
                    pass
        
        if valid_respondents:
            respondent, total_years = random.choice(valid_respondents)
            
            question = template.format(feature=target_feature, total=int(total_years))
            answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
            
            feature_values = extract_feature_values(case_respondents, selected_features)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': selected_features,
                'target_respondent': respondent['respondent'],
                'developer_name': 'N/A',
                'reasoning_complexity': 4,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'experience_total_calculation',
                    'years_code': respondent['answers']['YearsCode'],
                    'years_code_pro': respondent['answers']['YearsCodePro'],
                    'total_years': total_years
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    numeric_features = ['YearsCode', 'YearsCodePro', 'CompTotal']
    categorical_features = ['MainBranch', 'Employment', 'EdLevel', 'Country']
    
    template = "What is the {feature} of the respondent whose {numeric_feature} is {comparison} than the average {numeric_feature} for all respondents with {group_feature} = '{group_value}' in this case?"
    
    target_feature = random.choice(features)
    
    if numeric_features and categorical_features:
        numeric_feature = random.choice(numeric_features)
        group_feature = random.choice([f for f in categorical_features if f != target_feature])
        selected_features = [target_feature, numeric_feature, group_feature]
        
        # Get possible group values within this case
        possible_groups = list(set([r['answers'].get(group_feature) for r in case_respondents 
                                  if r['answers'].get(group_feature) is not None]))
        
        if possible_groups:
            group_value = random.choice(possible_groups)
            comparison = random.choice(['higher', 'lower'])
            
            # Calculate average for this group within this case
            group_stats = calculate_group_statistics(case_respondents, numeric_feature, group_feature, group_value)
            group_avg = group_stats['average']
            
            # Find respondents in this group whose value is above/below average within this case
            target_respondents = []
            for resp in case_respondents:
                resp_group_val = resp['answers'].get(group_feature)
                if resp_group_val == group_value:
                    numeric_val = resp['answers'].get(numeric_feature)
                    if numeric_val is not None:
                        try:
                            numeric_val = float(numeric_val)
                            if ((comparison == 'higher' and numeric_val > group_avg) or
                                (comparison == 'lower' and numeric_val < group_avg)):
                                target_respondents.append((resp, numeric_val))
                        except (ValueError, TypeError):
                            pass
            
            if target_respondents:
                # Pick one of the qualifying respondents
                respondent, respondent_value = random.choice(target_respondents)
                decoded_group_value = decode_mcq_answer(group_feature, group_value, questions_schema)
                
                question = template.format(
                    feature=target_feature, numeric_feature=numeric_feature,
                    comparison=comparison, group_feature=group_feature, 
                    group_value=decoded_group_value
                )
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'developer_name': 'N/A',
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'above_below_average_in_group_within_case',
                        'numeric_feature': numeric_feature,
                        'group_feature': group_feature,
                        'group_value': {'raw': group_value, 'decoded': decoded_group_value},
                        'group_average': group_avg,
                        'comparison': comparison,
                        'respondent_value': respondent_value,
                        'qualifying_candidates': len(target_respondents),
                        'group_statistics': group_stats
                    }
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for stack-overflow-2022 answer lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stack-overflow-2022_answer_lookup_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names from the questions schema
    features = [f for f in sample_data['questions'].keys() if f != 'respondent']
    print(f"Loaded {len(features)} features: {features}")
    
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