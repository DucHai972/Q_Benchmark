#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

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
        if value is not None and value != -1:  # Skip missing values (-1)
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
    group_respondents = [r for r in respondents 
                        if r['answers'].get(group_feature) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(feature)
        if value is not None and value != -1:  # Skip missing values
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

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Score features (rubric-based)
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    # Non-score features 
    other_features = ['Date', 'SessionName', 'Comments']
    
    templates = [
        ("direct_respondent", "What is the {feature} of respondent '{respondent_id}'?"),
        ("session_date", "What is the {feature} of the respondent from the '{session_name}' session on '{date}'?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    selected_features = [target_feature]
    
    if template_type == "direct_respondent":
        # Pick a random respondent from this case
        respondent = random.choice(case_respondents)
        question = template.format(feature=target_feature, respondent_id=respondent['respondent'])
        answer = str(respondent['answers'][target_feature])
        
        feature_values = extract_feature_values(case_respondents, selected_features)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': selected_features,
            'target_respondent': respondent['respondent'],
            'reasoning_complexity': 1,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'direct_lookup',
                'target_value': respondent['answers'][target_feature]
            }
        }
        
    else:  # session_date
        # Find a respondent with both session name and date
        valid_respondents = [r for r in case_respondents 
                           if r['answers'].get('SessionName') and r['answers'].get('Date')]
        if valid_respondents:
            respondent = random.choice(valid_respondents)
            session_name = respondent['answers']['SessionName']
            date = respondent['answers']['Date']
            selected_features = [target_feature, 'SessionName', 'Date']
            
            question = template.format(feature=target_feature, session_name=session_name, date=date)
            answer = str(respondent['answers'][target_feature])
            
            feature_values = extract_feature_values(case_respondents, selected_features)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': selected_features,
                'target_respondent': respondent['respondent'],
                'reasoning_complexity': 2,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_date_filter',
                    'filter_conditions': {
                        'SessionName': session_name,
                        'Date': date
                    }
                }
            }
    
    # Fallback to direct respondent
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("highest_in_session", "What is the {feature} of the respondent with the highest {score_type} in the '{session_name}' session?"),
        ("score_combination", "What is the {feature} of the respondent whose score for '{score_a}' was {value_a} and score for '{score_b}' was {value_b}?"),
        ("total_score", "What is the {feature} of the respondent whose total score for '{score_a}' and '{score_b}' was exactly {total}?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    
    if template_type == "highest_in_session":
        # Find highest score within a specific session within this case
        score_feature = random.choice(score_features)
        possible_sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                    if r['answers'].get('SessionName')]))
        
        if possible_sessions:
            session_name = random.choice(possible_sessions)
            selected_features = [target_feature, score_feature, 'SessionName']
            
            # Find highest score in this session within this case
            filters = {'SessionName': session_name}
            respondent, score_value = find_superlative_respondent(case_respondents, score_feature, 'max', filters)
            
            if respondent:
                question = template.format(feature=target_feature, score_type=score_feature, session_name=session_name)
                answer = str(respondent['answers'][target_feature])
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                session_stats = calculate_group_statistics(case_respondents, score_feature, 'SessionName', session_name)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'session_superlative',
                        'score_feature': score_feature,
                        'session_name': session_name,
                        'superlative_value': score_value,
                        'session_statistics': session_stats
                    }
                }
    
    elif template_type == "score_combination":
        # Find respondent with specific score combination within this case
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            selected_features = [target_feature, score_a, score_b]
            
            # Find a respondent with valid scores for both features within this case
            valid_respondents = [r for r in case_respondents 
                               if (r['answers'].get(score_a) is not None and r['answers'].get(score_a) != -1 and
                                   r['answers'].get(score_b) is not None and r['answers'].get(score_b) != -1)]
            
            if valid_respondents:
                respondent = random.choice(valid_respondents)
                value_a = respondent['answers'][score_a]
                value_b = respondent['answers'][score_b]
                
                question = template.format(feature=target_feature, score_a=score_a, 
                                         value_a=value_a, score_b=score_b, value_b=value_b)
                answer = str(respondent['answers'][target_feature])
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'score_combination_filter',
                        'filter_conditions': {
                            score_a: value_a,
                            score_b: value_b
                        }
                    }
                }
    
    elif template_type == "total_score":
        # Find respondent with specific total score within this case
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            selected_features = [target_feature, score_a, score_b]
            
            # Calculate totals for all respondents in this case
            valid_respondents = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_a)
                val_b = resp['answers'].get(score_b)
                if (val_a is not None and val_a != -1 and 
                    val_b is not None and val_b != -1):
                    try:
                        total = float(val_a) + float(val_b)
                        valid_respondents.append((resp, total))
                    except (ValueError, TypeError):
                        pass
            
            if valid_respondents:
                respondent, total_score = random.choice(valid_respondents)
                
                question = template.format(feature=target_feature, score_a=score_a, 
                                         score_b=score_b, total=int(total_score))
                answer = str(respondent['answers'][target_feature])
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'total_score_calculation',
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
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    template = "What is the {feature} of the respondent from the '{session_name}' session whose {score_type} is higher than the average {score_type} for all sessions on '{date}'?"
    
    target_feature = random.choice(features)
    score_feature = random.choice(score_features)
    
    # Get possible dates within this case
    possible_dates = list(set([r['answers'].get('Date') for r in case_respondents 
                             if r['answers'].get('Date')]))
    
    if possible_dates:
        target_date = random.choice(possible_dates)
        selected_features = [target_feature, score_feature, 'SessionName', 'Date']
        
        # Calculate average score for all sessions on this date within this case
        date_respondents = [r for r in case_respondents 
                          if r['answers'].get('Date') == target_date]
        
        date_scores = []
        for resp in date_respondents:
            score = resp['answers'].get(score_feature)
            if score is not None and score != -1:
                try:
                    date_scores.append(float(score))
                except (ValueError, TypeError):
                    pass
        
        if date_scores:
            date_average = statistics.mean(date_scores)
            
            # Find respondents on this date whose score is above average within this case
            above_avg_respondents = []
            for resp in date_respondents:
                score = resp['answers'].get(score_feature)
                session_name = resp['answers'].get('SessionName')
                if (score is not None and score != -1 and session_name and
                    float(score) > date_average):
                    above_avg_respondents.append((resp, float(score)))
            
            if above_avg_respondents:
                # Pick one of the above-average respondents
                respondent, score_value = random.choice(above_avg_respondents)
                session_name = respondent['answers']['SessionName']
                
                question = template.format(
                    feature=target_feature, session_name=session_name,
                    score_type=score_feature, date=target_date
                )
                answer = str(respondent['answers'][target_feature])
                
                feature_values = extract_feature_values(case_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'above_average_by_date_in_case',
                        'score_feature': score_feature,
                        'target_date': target_date,
                        'session_name': session_name,
                        'date_average': date_average,
                        'respondent_score': score_value,
                        'above_average_candidates': len(above_avg_respondents),
                        'date_statistics': {
                            'count': len(date_scores),
                            'average': date_average,
                            'all_scores': date_scores
                        }
                    }
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for isbar answer lookup using case-specific data."""
    
    # Paths
    features_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_features.json"
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_answer_lookup_qa.json"
    
    # Load features from actual data structure (not the features.json)
    # Check a sample case to get the actual field names
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