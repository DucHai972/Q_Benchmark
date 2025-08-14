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

def find_respondents_by_score_range(respondents, field, min_score, max_score):
    """Find all respondents with score in given range within this case."""
    matching_respondents = []
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None and value != -1:  # Skip missing values (-1)
            try:
                numeric_value = float(value)
                if min_score <= numeric_value <= max_score:
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_by_total_score(respondents, fields, threshold, comparison='greater'):
    """Find all respondents with combined score compared to threshold within this case."""
    matching_respondents = []
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in fields:
            value = resp['answers'].get(field)
            if value is not None and value != -1:
                try:
                    total_score += float(value)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        # Only consider if all scores are available
        if valid_scores == len(fields):
            if ((comparison == 'greater' and total_score > threshold) or
                (comparison == 'less' and total_score < threshold) or
                (comparison == 'equal' and total_score == threshold)):
                matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_comment_keyword(respondents, keyword):
    """Find all respondents whose comments contain the keyword within this case."""
    matching_respondents = []
    
    for resp in respondents:
        comments = resp['answers'].get('Comments', '')
        if comments and isinstance(comments, str) and keyword.lower() in comments.lower():
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def calculate_average_for_group(respondents, target_field, group_field, group_value):
    """Calculate average of target_field for respondents in specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(target_field)
        if value is not None and value != -1:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_session_averages(respondents, score_field):
    """Calculate averages for each session name within this case."""
    session_averages = {}
    
    # Group by session name
    sessions = {}
    for resp in respondents:
        session_name = resp['answers'].get('SessionName')
        if session_name:
            if session_name not in sessions:
                sessions[session_name] = []
            sessions[session_name].append(resp)
    
    # Calculate averages
    for session_name, session_respondents in sessions.items():
        values = []
        for resp in session_respondents:
            value = resp['answers'].get(score_field)
            if value is not None and value != -1:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass
        
        session_averages[session_name] = statistics.mean(values) if values else 0
    
    return session_averages

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Score features (rubric-based, 0-3 scale)
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    # Context features
    context_features = ['Date', 'SessionName', 'Comments']
    
    templates = [
        ("session_participants", "Which respondents participated in a '{session_name}' session?"),
        ("score_match", "Find all respondents who scored {score} on '{score_type}'."),
        ("date_score_combo", "List all respondents from sessions on '{date}' who scored {score} on '{score_type}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_participants":
        # Find all respondents from specific session
        possible_sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                    if r['answers'].get('SessionName') is not None]))
        
        if possible_sessions:
            session_name = random.choice(possible_sessions)
            matching_respondents = find_respondents_by_criteria(case_respondents, {'SessionName': session_name})
            
            question = template.format(session_name=session_name)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['SessionName'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_filter',
                    'criteria': {'SessionName': session_name},
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "score_match":
        # Find all respondents with specific score
        if score_features:
            score_type = random.choice(score_features)
            
            # Get possible scores (0-3) from this case
            possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                      if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
            
            if possible_scores:
                score = random.choice(possible_scores)
                matching_respondents = find_respondents_by_criteria(case_respondents, {score_type: score})
                
                question = template.format(score=score, score_type=score_type)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [score_type])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_type],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 1,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'score_filter',
                        'criteria': {score_type: score},
                        'matches_found': len(matching_respondents)
                    }
                }
    
    else:  # date_score_combo
        # Find respondents by date and score combination
        if score_features:
            score_type = random.choice(score_features)
            
            # Get possible dates and scores from this case
            possible_dates = list(set([r['answers'].get('Date') for r in case_respondents 
                                     if r['answers'].get('Date') is not None]))
            possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                      if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
            
            if possible_dates and possible_scores:
                date = random.choice(possible_dates)
                score = random.choice(possible_scores)
                
                criteria = {'Date': date, score_type: score}
                matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(date=date, score=score, score_type=score_type)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Date', score_type])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Date', score_type],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'date_score_filter',
                        'criteria': criteria,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("session_multi_scores", "Find all respondents from the '{session_name}' session who scored {score_a} on '{score_type_a}' and {score_b} on '{score_type_b}'."),
        ("total_score_threshold", "Which respondents have a total score for '{score_type_a}' and '{score_type_b}' greater than {threshold}?"),
        ("score_comment_combo", "List all respondents who scored {score} on '{score_type}' and whose 'Comments' contain the word '{keyword}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_multi_scores":
        # Find respondents from specific session with multiple score criteria
        possible_sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                    if r['answers'].get('SessionName') is not None]))
        
        if possible_sessions and len(score_features) >= 2:
            session_name = random.choice(possible_sessions)
            score_type_a, score_type_b = random.sample(score_features, 2)
            
            # Get possible scores for each type from this session within this case
            session_respondents = [r for r in case_respondents if r['answers'].get('SessionName') == session_name]
            
            scores_a = list(set([r['answers'].get(score_type_a) for r in session_respondents 
                               if r['answers'].get(score_type_a) is not None and r['answers'].get(score_type_a) != -1]))
            scores_b = list(set([r['answers'].get(score_type_b) for r in session_respondents 
                               if r['answers'].get(score_type_b) is not None and r['answers'].get(score_type_b) != -1]))
            
            if scores_a and scores_b:
                score_a = random.choice(scores_a)
                score_b = random.choice(scores_b)
                
                criteria = {'SessionName': session_name, score_type_a: score_a, score_type_b: score_b}
                matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(session_name=session_name, score_a=score_a, 
                                         score_type_a=score_type_a, score_b=score_b, score_type_b=score_type_b)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['SessionName', score_type_a, score_type_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['SessionName', score_type_a, score_type_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'session_multi_score_filter',
                        'criteria': criteria,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "total_score_threshold":
        # Find respondents with combined score above threshold
        if len(score_features) >= 2:
            score_type_a, score_type_b = random.sample(score_features, 2)
            
            # Calculate reasonable threshold based on available scores within this case
            total_scores = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_type_a)
                val_b = resp['answers'].get(score_type_b)
                if val_a is not None and val_a != -1 and val_b is not None and val_b != -1:
                    try:
                        total = float(val_a) + float(val_b)
                        total_scores.append(total)
                    except (ValueError, TypeError):
                        pass
            
            if total_scores:
                threshold = int(statistics.median(total_scores))
                matching_respondents = find_respondents_by_total_score(case_respondents, [score_type_a, score_type_b], threshold, 'greater')
                
                question = template.format(score_type_a=score_type_a, score_type_b=score_type_b, threshold=threshold)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [score_type_a, score_type_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_type_a, score_type_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'total_score_threshold',
                        'score_fields': [score_type_a, score_type_b],
                        'threshold': threshold,
                        'comparison': 'greater',
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "score_comment_combo":
        # Find respondents with specific score and comment keyword
        if score_features:
            score_type = random.choice(score_features)
            
            # Get possible scores and keywords from this case
            possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                      if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
            
            # Extract common words from comments
            keywords = []
            for resp in case_respondents:
                comments = resp['answers'].get('Comments', '')
                if comments and isinstance(comments, str):
                    words = [word.strip('.,!?()') for word in comments.split() if len(word.strip('.,!?()')) > 3]
                    keywords.extend(words)
            
            common_keywords = ['Good', 'Clear', 'Overall', 'Time', 'communication', 'unclear', 'reflected']
            
            if possible_scores and keywords:
                score = random.choice(possible_scores)
                keyword = random.choice(common_keywords)
                
                # Find respondents matching both criteria
                score_matches = find_respondents_by_criteria(case_respondents, {score_type: score})
                comment_matches = find_respondents_by_comment_keyword(case_respondents, keyword)
                matching_respondents = list(set(score_matches) & set(comment_matches))
                
                question = template.format(score=score, score_type=score_type, keyword=keyword)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [score_type, 'Comments'])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_type, 'Comments'],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'score_comment_combination',
                        'score_criteria': {score_type: score},
                        'keyword': keyword,
                        'score_matches': len(score_matches),
                        'comment_matches': len(comment_matches),
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
        ("above_date_average", "Find all respondents whose '{score_type}' is higher than the average '{score_type}' for all sessions on the same date."),
        ("high_average_session", "Which respondents participated in a session where the average '{score_type}' for that session name is greater than {threshold}?"),
        ("perfect_score_below_average", "List all respondents who scored perfectly on '{score_type_a}' and '{score_type_b}' and whose '{score_type_c}' is below the average for all sessions.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_date_average":
        # Find respondents above average for their date
        if score_features:
            score_type = random.choice(score_features)
            matching_respondents = []
            
            # Calculate averages by date within this case
            date_averages = {}
            dates = list(set([r['answers'].get('Date') for r in case_respondents 
                            if r['answers'].get('Date') is not None]))
            
            for date in dates:
                date_average = calculate_average_for_group(case_respondents, score_type, 'Date', date)
                date_averages[date] = date_average
            
            # Find respondents above their date average
            for resp in case_respondents:
                date = resp['answers'].get('Date')
                score = resp['answers'].get(score_type)
                
                if date and score is not None and score != -1 and date in date_averages:
                    try:
                        if float(score) > date_averages[date]:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(score_type=score_type)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [score_type, 'Date'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': [score_type, 'Date'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_date_average',
                    'score_type': score_type,
                    'date_averages': date_averages,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "high_average_session":
        # Find respondents in sessions with high average scores
        if score_features:
            score_type = random.choice(score_features)
            
            # Calculate session averages within this case
            session_averages = calculate_session_averages(case_respondents, score_type)
            
            if session_averages:
                threshold = random.choice([2.0, 2.5])  # High threshold for good sessions
                
                # Find sessions above threshold
                qualifying_sessions = [session for session, avg in session_averages.items() if avg > threshold]
                
                # Find all respondents in those sessions
                matching_respondents = []
                for resp in case_respondents:
                    session = resp['answers'].get('SessionName')
                    if session in qualifying_sessions:
                        matching_respondents.append(resp['respondent'])
                
                question = template.format(score_type=score_type, threshold=threshold)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [score_type, 'SessionName'])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_type, 'SessionName'],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'high_average_session',
                        'score_type': score_type,
                        'threshold': threshold,
                        'session_averages': session_averages,
                        'qualifying_sessions': qualifying_sessions,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "perfect_score_below_average":
        # Find respondents with perfect scores on two features but below average on third
        if len(score_features) >= 3:
            score_type_a, score_type_b, score_type_c = random.sample(score_features, 3)
            
            # Calculate overall average for score_type_c within this case
            overall_average = calculate_average_for_group(case_respondents, score_type_c, 'Date', None)
            if overall_average == 0:  # If date grouping fails, calculate simple average
                values = []
                for resp in case_respondents:
                    val = resp['answers'].get(score_type_c)
                    if val is not None and val != -1:
                        try:
                            values.append(float(val))
                        except (ValueError, TypeError):
                            pass
                overall_average = statistics.mean(values) if values else 0
            
            # Find respondents with perfect scores (3) on A and B, but below average on C
            matching_respondents = []
            for resp in case_respondents:
                score_a = resp['answers'].get(score_type_a)
                score_b = resp['answers'].get(score_type_b)
                score_c = resp['answers'].get(score_type_c)
                
                if (score_a == 3 and score_b == 3 and 
                    score_c is not None and score_c != -1):
                    try:
                        if float(score_c) < overall_average:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(score_type_a=score_type_a, score_type_b=score_type_b, score_type_c=score_type_c)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [score_type_a, score_type_b, score_type_c])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': [score_type_a, score_type_b, score_type_c],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'perfect_scores_below_average',
                    'perfect_score_fields': [score_type_a, score_type_b],
                    'below_average_field': score_type_c,
                    'overall_average': overall_average,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for isbar answer reverse lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/answer_reverse_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_answer_reverse_lookup_qa.json"
    
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