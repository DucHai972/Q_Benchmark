#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

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
                    elif condition_comparison == 'perfect' and value == 3:  # Perfect score is 3
                        matching_respondents.append(resp_id)
                    elif condition_comparison == 'contains':
                        comments = resp['answers'].get('Comments', '')
                        if comments and isinstance(comments, str) and condition_value.lower() in comments.lower():
                            matching_respondents.append(resp_id)
                break
    
    return matching_respondents

def calculate_average_for_date(respondents, date, score_field):
    """Calculate average score for all sessions on a specific date within this case."""
    date_respondents = [r for r in respondents if r['answers'].get('Date') == date]
    
    values = []
    for resp in date_respondents:
        value = resp['answers'].get(score_field)
        if value is not None and value != -1:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_for_session_name(respondents, session_name, score_field):
    """Calculate average score for specific session name within this case."""
    session_respondents = [r for r in respondents if r['answers'].get('SessionName') == session_name]
    
    values = []
    for resp in session_respondents:
        value = resp['answers'].get(score_field)
        if value is not None and value != -1:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_total_rubric_score(respondent):
    """Calculate total score across all rubric items for a respondent."""
    rubric_fields = ['Identification', 'Situation', 'Background (history)', 
                    'Background (examination)', 'Assessment', 
                    'Recommendation (clear recommendation)', 
                    'Recommendation (global rating scale)']
    
    total = 0
    valid_scores = 0
    
    for field in rubric_fields:
        value = respondent['answers'].get(field)
        if value is not None and value != -1:
            try:
                total += float(value)
                valid_scores += 1
            except (ValueError, TypeError):
                pass
    
    return total if valid_scores > 0 else 0

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Score features (rubric-based, 0-3 scale)
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("same_session", "Which respondents participated in the same session name as respondent '{target_id}'?"),
        ("same_date", "Find all respondents who had a session on the same date as respondent '{target_id}', excluding the respondent themselves."),
        ("same_score", "List all respondents who scored the same on '{score_type}' as respondent '{target_id}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "same_session":
        feature = 'SessionName'
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
    
    elif template_type == "same_date":
        feature = 'Date'
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
    
    else:  # same_score
        score_type = random.choice(score_features)
        matching_respondents = find_respondents_with_same_feature(case_respondents, target_id, score_type, exclude_self=True)
        
        question = template.format(target_id=target_id, score_type=score_type)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_type],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 2,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_score_hop',
                'target_respondent': target_id,
                'shared_feature': score_type,
                'target_score_value': target_respondent['answers'].get(score_type),
                'matches_found': len(matching_respondents)
            }
        }

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("date_and_score", "Which respondents had a session on the same date as respondent '{target_id}' and also scored {score_value} on '{score_type}'?"),
        ("session_and_keyword", "Find all respondents who participated in the same session name as respondent '{target_id}' and whose comments contain the word '{keyword}'."),
        ("score_and_perfect", "List all respondents who scored the same on '{score_a}' as respondent '{target_id}' and also scored perfectly on '{score_b}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "date_and_score":
        shared_feature = 'Date'
        condition_field = random.choice(score_features)
        condition_value = random.choice([0, 1, 2, 3])  # Valid rubric scores
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, condition_value, 'equal'
        )
        
        question = template.format(target_id=target_id, score_value=condition_value, score_type=condition_field)
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
                'condition_value': condition_value,
                'condition_comparison': 'equal',
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "session_and_keyword":
        shared_feature = 'SessionName'
        keywords = ['Good', 'Clear', 'Satisfactory', 'Overall', 'Time', 'communication', 'unclear']
        keyword = random.choice(keywords)
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, 'Comments', keyword, 'contains'
        )
        
        question = template.format(target_id=target_id, keyword=keyword)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [shared_feature, 'Comments'],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_plus_keyword',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'keyword': keyword,
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # score_and_perfect
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            
            # Find respondents with same score on A as target
            same_score_a = find_respondents_with_same_feature(case_respondents, target_id, score_a, exclude_self=True)
            
            # Filter those who also scored perfectly (3) on score B
            matching_respondents = []
            for resp_id in same_score_a:
                for resp in case_respondents:
                    if resp['respondent'] == resp_id:
                        score_b_value = resp['answers'].get(score_b)
                        if score_b_value == 3:  # Perfect score
                            matching_respondents.append(resp_id)
                        break
            
            question = template.format(target_id=target_id, score_a=score_a, score_b=score_b)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'target_respondent': target_id,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'same_score_plus_perfect',
                    'target_respondent': target_id,
                    'shared_score': score_a,
                    'perfect_score_field': score_b,
                    'target_score_value': target_respondent['answers'].get(score_a),
                    'matches_found': len(matching_respondents)
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
    
    templates = [
        ("above_date_average", "Find all respondents whose '{score_type}' is higher than the average '{score_type}' for all sessions that happened on the same date as respondent '{target_id}'s session."),
        ("session_above_overall", "Which respondents are from a session name where the average '{score_type}' score is higher than the overall average for all sessions?"),
        ("below_date_total_average", "List all respondents whose total score across all rubric items is lower than the average total score for all sessions on '{specific_date}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_date_average":
        # Choose a random respondent as target and score type
        if not case_respondents:
            return None
        
        target_respondent = random.choice(case_respondents)
        target_id = target_respondent['respondent']
        target_date = target_respondent['answers'].get('Date')
        score_type = random.choice(score_features)
        
        if target_date:
            # Calculate average score for that date
            date_average = calculate_average_for_date(case_respondents, target_date, score_type)
            
            # Find respondents above this average
            matching_respondents = []
            for resp in case_respondents:
                score = resp['answers'].get(score_type)
                if score is not None and score != -1:
                    try:
                        if float(score) > date_average:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(target_id=target_id, score_type=score_type)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Date', score_type],
                'target_respondent': target_id,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_date_average',
                    'target_respondent': target_id,
                    'target_date': target_date,
                    'score_type': score_type,
                    'date_average': date_average,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "session_above_overall":
        score_type = random.choice(score_features)
        
        # Calculate overall average for this score type
        all_scores = []
        for resp in case_respondents:
            score = resp['answers'].get(score_type)
            if score is not None and score != -1:
                try:
                    all_scores.append(float(score))
                except (ValueError, TypeError):
                    pass
        
        if all_scores:
            overall_average = statistics.mean(all_scores)
            
            # Find session names with above-average scores
            session_names = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                    if r['answers'].get('SessionName') is not None]))
            
            qualifying_sessions = []
            for session in session_names:
                session_average = calculate_average_for_session_name(case_respondents, session, score_type)
                if session_average > overall_average:
                    qualifying_sessions.append(session)
            
            # Find all respondents in qualifying sessions
            matching_respondents = []
            for resp in case_respondents:
                session = resp['answers'].get('SessionName')
                if session in qualifying_sessions:
                    matching_respondents.append(resp['respondent'])
            
            question = template.format(score_type=score_type)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName', score_type],
                'target_respondent': None,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_above_overall_average',
                    'score_type': score_type,
                    'overall_average': overall_average,
                    'qualifying_sessions': qualifying_sessions,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "below_date_total_average":
        # Choose a specific date that exists in the data
        dates = list(set([r['answers'].get('Date') for r in case_respondents 
                        if r['answers'].get('Date') is not None]))
        
        if dates:
            specific_date = random.choice(dates)
            
            # Calculate average total score for that date
            date_respondents = [r for r in case_respondents if r['answers'].get('Date') == specific_date]
            date_total_scores = []
            for resp in date_respondents:
                total = calculate_total_rubric_score(resp)
                if total > 0:
                    date_total_scores.append(total)
            
            if date_total_scores:
                date_average_total = statistics.mean(date_total_scores)
                
                # Find respondents below this average
                matching_respondents = []
                for resp in case_respondents:
                    total = calculate_total_rubric_score(resp)
                    if total < date_average_total:
                        matching_respondents.append(resp['respondent'])
                
                question = template.format(specific_date=specific_date)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Date'] + score_features,
                    'target_respondent': None,
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 5,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'below_date_total_average',
                        'specific_date': specific_date,
                        'date_average_total': date_average_total,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for isbar multi hop relational inference using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/multi_hop_relational_inference/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_multi_hop_relational_qa.json"
    
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