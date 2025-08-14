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
    
    # Parse options like "A. Senior B. Junior C. Middle D. Intern"
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
        
    # Get numeric values for comparison (SUS scores are 1-5)
    valid_respondents = []
    for resp in filtered_respondents:
        value = resp['answers'].get(feature)
        if value is not None:
            try:
                numeric_value = float(value)
                valid_respondents.append((resp, numeric_value))
            except (ValueError, TypeError):
                # Skip non-numeric values
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

def generate_user_name():
    """Generate a random user name with varied case formatting."""
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
    # Usability score features (all Likert 1-5)
    score_features = [f for f in features if f != 'Group']
    
    templates = [
        ("direct_respondent", "What is the {feature} of respondent '{respondent_id}'?"),
        ("group_by_score", "What is the Group of the respondent who rated {score_feature} as {score_value}?"),
        ("score_by_group", "What is the {feature} of the respondent from the {group_name} group?")
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
            'user_name': 'N/A',
            'reasoning_complexity': 1,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'direct_lookup',
                'target_value': respondent['answers'][target_feature]
            }
        }
        
    elif template_type == "group_by_score":
        # Find group of user who gave specific score within this case
        if score_features:
            score_feature = random.choice(score_features)
            selected_features = ['Group', score_feature]
            
            # Find possible score values within this case
            possible_scores = list(set([r['answers'].get(score_feature) for r in case_respondents 
                                      if r['answers'].get(score_feature) is not None]))
            
            if possible_scores:
                score_value = random.choice(possible_scores)
                
                # Find respondent with this score
                matching_respondents = [r for r in case_respondents 
                                      if r['answers'].get(score_feature) == score_value]
                
                if matching_respondents:
                    respondent = random.choice(matching_respondents)
                    
                    question = template.format(score_feature=score_feature, score_value=score_value)
                    answer = decode_mcq_answer('Group', respondent['answers']['Group'], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Easy",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'user_name': 'N/A',
                        'reasoning_complexity': 2,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'score_to_group_lookup',
                            'score_feature': score_feature,
                            'score_value': score_value
                        }
                    }
        
        # Fallback to direct respondent
        return generate_easy_question(case_id, case_respondents, features, questions_schema)
    
    else:  # score_by_group
        # Find score of user from specific group within this case
        selected_features = [target_feature, 'Group']
        
        # Find possible groups within this case
        possible_groups = list(set([r['answers'].get('Group') for r in case_respondents 
                                  if r['answers'].get('Group') is not None]))
        
        if possible_groups:
            group_code = random.choice(possible_groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            
            # Find respondent from this group
            group_respondents = [r for r in case_respondents 
                               if r['answers'].get('Group') == group_code]
            
            if group_respondents:
                respondent = random.choice(group_respondents)
                
                question = template.format(feature=target_feature, group_name=group_name)
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'user_name': 'N/A',
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'group_to_score_lookup',
                        'group_feature': 'Group',
                        'group_value': {'raw': group_code, 'decoded': group_name}
                    }
                }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = [f for f in features if f != 'Group']
    
    templates = [
        ("superlative_in_group", "What is the {feature} of the respondent from the {group_name} group with the {superlative} {score_feature} score?"),
        ("multi_score_condition", "What is the {feature} of the respondent from the {group_name} group who rated {score_a} as {value_a} and {score_b} as {value_b}?"),
        ("combined_score", "What is the {feature} of the respondent whose combined score for {score_a} and {score_b} was exactly {total}?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    
    if template_type == "superlative_in_group":
        # Find superlative score within a specific group within this case
        if score_features:
            score_feature = random.choice(score_features)
            selected_features = [target_feature, score_feature, 'Group']
            
            # Find possible groups within this case
            possible_groups = list(set([r['answers'].get('Group') for r in case_respondents 
                                      if r['answers'].get('Group') is not None]))
            
            if possible_groups:
                group_code = random.choice(possible_groups)
                group_name = decode_mcq_answer('Group', group_code, questions_schema)
                superlative = random.choice(['highest', 'lowest'])
                mode = 'max' if superlative == 'highest' else 'min'
                
                # Find superlative in this group within this case
                filters = {'Group': group_code}
                respondent, score_value = find_superlative_respondent(case_respondents, score_feature, mode, filters)
                
                if respondent:
                    question = template.format(feature=target_feature, group_name=group_name, 
                                             superlative=superlative, score_feature=score_feature)
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    group_stats = calculate_group_statistics(case_respondents, score_feature, 'Group', group_code)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'user_name': 'N/A',
                        'reasoning_complexity': 3,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'group_superlative',
                            'score_feature': score_feature,
                            'superlative_type': mode,
                            'superlative_value': score_value,
                            'group_value': {'raw': group_code, 'decoded': group_name},
                            'group_statistics': group_stats
                        }
                    }
    
    elif template_type == "multi_score_condition":
        # Find respondent in specific group with multiple score conditions within this case
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            selected_features = [target_feature, 'Group', score_a, score_b]
            
            # Find possible groups within this case
            possible_groups = list(set([r['answers'].get('Group') for r in case_respondents 
                                      if r['answers'].get('Group') is not None]))
            
            if possible_groups:
                group_code = random.choice(possible_groups)
                group_name = decode_mcq_answer('Group', group_code, questions_schema)
                
                # Find a respondent in this group with valid scores for both features within this case
                group_respondents = [r for r in case_respondents 
                                   if r['answers'].get('Group') == group_code]
                
                valid_respondents = [r for r in group_respondents 
                                   if r['answers'].get(score_a) and r['answers'].get(score_b)]
                
                if valid_respondents:
                    respondent = random.choice(valid_respondents)
                    value_a = respondent['answers'][score_a]
                    value_b = respondent['answers'][score_b]
                    
                    question = template.format(feature=target_feature, group_name=group_name, 
                                             score_a=score_a, value_a=value_a, 
                                             score_b=score_b, value_b=value_b)
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(case_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'user_name': 'N/A',
                        'reasoning_complexity': 4,
                        'feature_values': feature_values,
                        'case_respondent_count': len(case_respondents),
                        'calculation_details': {
                            'method': 'multi_score_group_filter',
                            'group_value': {'raw': group_code, 'decoded': group_name},
                            'filter_conditions': {
                                score_a: value_a,
                                score_b: value_b
                            }
                        }
                    }
    
    elif template_type == "combined_score":
        # Find respondent with specific combined score within this case
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            selected_features = [target_feature, score_a, score_b]
            
            # Calculate combined scores for all respondents in this case
            valid_respondents = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_a)
                val_b = resp['answers'].get(score_b)
                if val_a and val_b:
                    try:
                        total = float(val_a) + float(val_b)
                        valid_respondents.append((resp, total))
                    except (ValueError, TypeError):
                        pass
            
            if valid_respondents:
                respondent, total_score = random.choice(valid_respondents)
                
                question = template.format(feature=target_feature, score_a=score_a, 
                                         score_b=score_b, total=int(total_score))
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'user_name': 'N/A',
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'combined_score_calculation',
                        'score_features': [score_a, score_b],
                        'individual_scores': {
                            score_a: respondent['answers'][score_a],
                            score_b: respondent['answers'][score_b]
                        },
                        'total_score': total_score
                    }
                }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    score_features = [f for f in features if f != 'Group']
    
    template = "What is the {feature} of the respondent from the {group_a_name} group whose {score_feature} is {comparison} than the average {score_feature} for the {group_b_name} group in this case?"
    
    target_feature = random.choice(features)
    
    if score_features:
        score_feature = random.choice(score_features)
        selected_features = [target_feature, score_feature, 'Group']
        
        # Get possible groups within this case
        possible_groups = list(set([r['answers'].get('Group') for r in case_respondents 
                                  if r['answers'].get('Group') is not None]))
        
        if len(possible_groups) >= 2:
            group_a_code, group_b_code = random.sample(possible_groups, 2)
            group_a_name = decode_mcq_answer('Group', group_a_code, questions_schema)
            group_b_name = decode_mcq_answer('Group', group_b_code, questions_schema)
            comparison = random.choice(['higher', 'lower'])
            
            # Calculate average for group B within this case
            group_b_stats = calculate_group_statistics(case_respondents, score_feature, 'Group', group_b_code)
            group_b_avg = group_b_stats['average']
            
            # Find respondents in group A whose score is above/below group B average within this case
            target_respondents = []
            for resp in case_respondents:
                resp_group = resp['answers'].get('Group')
                if resp_group == group_a_code:
                    score_val = resp['answers'].get(score_feature)
                    if score_val is not None:
                        try:
                            score_val = float(score_val)
                            if ((comparison == 'higher' and score_val > group_b_avg) or
                                (comparison == 'lower' and score_val < group_b_avg)):
                                target_respondents.append((resp, score_val))
                        except (ValueError, TypeError):
                            pass
            
            if target_respondents:
                # Pick one of the qualifying respondents
                respondent, respondent_score = random.choice(target_respondents)
                
                question = template.format(
                    feature=target_feature, group_a_name=group_a_name,
                    score_feature=score_feature, comparison=comparison,
                    group_b_name=group_b_name
                )
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                group_a_stats = calculate_group_statistics(case_respondents, score_feature, 'Group', group_a_code)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'user_name': 'N/A',
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'cross_group_average_comparison_within_case',
                        'score_feature': score_feature,
                        'group_a': {'raw': group_a_code, 'decoded': group_a_name},
                        'group_b': {'raw': group_b_code, 'decoded': group_b_name},
                        'group_b_average': group_b_avg,
                        'comparison': comparison,
                        'respondent_score': respondent_score,
                        'qualifying_candidates': len(target_respondents),
                        'group_a_statistics': group_a_stats,
                        'group_b_statistics': group_b_stats
                    }
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for sus-uta7 answer lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus-uta7_answer_lookup_qa.json"
    
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