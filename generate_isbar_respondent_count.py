#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def count_respondents_with_session_name(respondents, session_name):
    """Count respondents who participated in specific session name."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('SessionName') == session_name:
            count += 1
    return count

def count_respondents_with_date(respondents, date):
    """Count respondents who participated in sessions on specific date."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('Date') == date:
            count += 1
    return count

def count_respondents_with_score(respondents, score_field, score_value):
    """Count respondents who scored specific value on score field."""
    count = 0
    for resp in respondents:
        score = resp['answers'].get(score_field)
        if score == score_value:
            count += 1
    return count

def count_respondents_with_date_and_score(respondents, date, score_field, score_value):
    """Count respondents from specific date with specific score."""
    count = 0
    for resp in respondents:
        if (resp['answers'].get('Date') == date and 
            resp['answers'].get(score_field) == score_value):
            count += 1
    return count

def count_respondents_with_multiple_scores(respondents, score_conditions):
    """Count respondents meeting multiple score conditions."""
    count = 0
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in score_conditions:
            field = condition['field']
            value = condition['value']
            
            resp_score = resp['answers'].get(field)
            if resp_score != value:
                meets_all_conditions = False
                break
        
        if meets_all_conditions:
            count += 1
    
    return count

def count_respondents_with_session_and_scores(respondents, session_name, score_conditions):
    """Count respondents from specific session with multiple score conditions."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('SessionName') != session_name:
            continue
            
        meets_all_scores = True
        for condition in score_conditions:
            field = condition['field']
            value = condition['value']
            
            resp_score = resp['answers'].get(field)
            if resp_score != value:
                meets_all_scores = False
                break
        
        if meets_all_scores:
            count += 1
    
    return count

def count_respondents_with_total_score_threshold(respondents, score_fields, threshold, comparison='greater'):
    """Count respondents whose total score across fields meets threshold."""
    count = 0
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in score_fields:
            score = resp['answers'].get(field)
            if score is not None and score != -1:  # -1 indicates missing data in ISBAR
                try:
                    total_score += float(score)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if valid_scores > 0:
            if comparison == 'greater' and total_score > threshold:
                count += 1
            elif comparison == 'less' and total_score < threshold:
                count += 1
            elif comparison == 'equal' and total_score == threshold:
                count += 1
    
    return count

def count_respondents_with_score_and_keyword(respondents, score_field, score_value, keyword):
    """Count respondents with specific score and keyword in comments."""
    count = 0
    for resp in respondents:
        score = resp['answers'].get(score_field)
        comments = resp['answers'].get('Comments', '')
        
        if (score == score_value and 
            comments and isinstance(comments, str) and 
            keyword.lower() in comments.lower()):
            count += 1
    
    return count

def calculate_average_score_for_date(respondents, date, score_field):
    """Calculate average score for specific date."""
    date_respondents = [r for r in respondents if r['answers'].get('Date') == date]
    
    values = []
    for resp in date_respondents:
        score = resp['answers'].get(score_field)
        if score is not None and score != -1:
            try:
                values.append(float(score))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_score_for_session(respondents, session_name, score_field):
    """Calculate average score for specific session name."""
    session_respondents = [r for r in respondents if r['answers'].get('SessionName') == session_name]
    
    values = []
    for resp in session_respondents:
        score = resp['answers'].get(score_field)
        if score is not None and score != -1:
            try:
                values.append(float(score))
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
        score = respondent['answers'].get(field)
        if score is not None and score != -1:
            try:
                total += float(score)
                valid_scores += 1
            except (ValueError, TypeError):
                pass
    
    return total if valid_scores > 0 else 0

def count_respondents_above_date_average(respondents, score_field):
    """Count respondents whose score is higher than average for their session date."""
    count = 0
    
    for resp in respondents:
        resp_date = resp['answers'].get('Date')
        resp_score = resp['answers'].get(score_field)
        
        if resp_date and resp_score is not None and resp_score != -1:
            try:
                resp_score_num = float(resp_score)
                date_average = calculate_average_score_for_date(respondents, resp_date, score_field)
                
                if resp_score_num > date_average:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_equal_date_average(respondents, score_field):
    """Count respondents whose score equals average for their session date."""
    count = 0
    
    for resp in respondents:
        resp_date = resp['answers'].get('Date')
        resp_score = resp['answers'].get(score_field)
        
        if resp_date and resp_score is not None and resp_score != -1:
            try:
                resp_score_num = float(resp_score)
                date_average = calculate_average_score_for_date(respondents, resp_date, score_field)
                
                if abs(resp_score_num - date_average) < 0.001:  # Float comparison with tolerance
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_in_high_average_sessions(respondents, score_field, threshold):
    """Count respondents in sessions where average score is greater than threshold."""
    count = 0
    
    # Get unique session names
    session_names = list(set([r['answers'].get('SessionName') for r in respondents 
                            if r['answers'].get('SessionName') is not None]))
    
    qualifying_sessions = []
    for session in session_names:
        session_avg = calculate_average_score_for_session(respondents, session, score_field)
        if session_avg > threshold:
            qualifying_sessions.append(session)
    
    # Count respondents in qualifying sessions
    for resp in respondents:
        session = resp['answers'].get('SessionName')
        if session in qualifying_sessions:
            count += 1
    
    return count

def count_respondents_below_overall_total_average(respondents):
    """Count respondents whose total score is below overall average."""
    # Calculate overall average total score
    all_totals = []
    for resp in respondents:
        total = calculate_total_rubric_score(resp)
        if total > 0:
            all_totals.append(total)
    
    if not all_totals:
        return 0
    
    overall_avg = statistics.mean(all_totals)
    
    # Count respondents below this average
    count = 0
    for resp in respondents:
        total = calculate_total_rubric_score(resp)
        if total < overall_avg:
            count += 1
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Score features (0-3 rubric scale)
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("session_name", "Count the respondents who participated in a '{session_name}' session."),
        ("date", "Count the respondents who participated in a session on '{date}'."),
        ("score", "Count the respondents who scored {score} on '{score_type}'."),
        ("date_and_score", "Count the respondents from sessions on '{date}' who scored {score} on '{score_type}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_name":
        # Get available session names
        session_names = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                if r['answers'].get('SessionName') is not None]))
        
        if session_names:
            session_name = random.choice(session_names)
            count = count_respondents_with_session_name(case_respondents, session_name)
            
            question = template.format(session_name=session_name)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName'],
                'filter_conditions': [{'field': 'SessionName', 'value': session_name}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_name_filter',
                    'session_name': session_name,
                    'matching_count': count
                }
            }
    
    elif template_type == "date":
        # Get available dates
        dates = list(set([r['answers'].get('Date') for r in case_respondents 
                         if r['answers'].get('Date') is not None]))
        
        if dates:
            date = random.choice(dates)
            count = count_respondents_with_date(case_respondents, date)
            
            question = template.format(date=date)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Date'],
                'filter_conditions': [{'field': 'Date', 'value': date}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'date_filter',
                    'date': date,
                    'matching_count': count
                }
            }
    
    elif template_type == "score":
        score_type = random.choice(score_features)
        score_value = random.choice([0, 1, 2, 3])  # Valid rubric scores
        
        count = count_respondents_with_score(case_respondents, score_type, score_value)
        
        question = template.format(score=score_value, score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_type],
            'filter_conditions': [{'field': score_type, 'value': score_value}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_filter',
                'score_field': score_type,
                'score_value': score_value,
                'matching_count': count
            }
        }
    
    else:  # date_and_score
        dates = list(set([r['answers'].get('Date') for r in case_respondents 
                         if r['answers'].get('Date') is not None]))
        
        if dates:
            date = random.choice(dates)
            score_type = random.choice(score_features)
            score_value = random.choice([0, 1, 2, 3])
            
            count = count_respondents_with_date_and_score(case_respondents, date, score_type, score_value)
            
            question = template.format(date=date, score=score_value, score_type=score_type)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Date', score_type],
                'filter_conditions': [
                    {'field': 'Date', 'value': date},
                    {'field': score_type, 'value': score_value}
                ],
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'date_and_score_filter',
                    'date': date,
                    'score_field': score_type,
                    'score_value': score_value,
                    'matching_count': count
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("session_multiple_scores", "Count the respondents from the '{session_name}' session who scored {score_a} on '{score_type_a}' and {score_b} on '{score_type_b}'."),
        ("total_score_threshold", "Count the respondents whose total score for '{score_type_a}' and '{score_type_b}' is greater than {threshold}."),
        ("score_with_keyword", "Count the respondents who scored {score} on '{score_type}' and whose 'Comments' contain the word '{keyword}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_multiple_scores":
        # Get available session names
        session_names = list(set([r['answers'].get('SessionName') for r in case_respondents 
                                if r['answers'].get('SessionName') is not None]))
        
        if session_names and len(score_features) >= 2:
            session_name = random.choice(session_names)
            score_type_a, score_type_b = random.sample(score_features, 2)
            score_a = random.choice([0, 1, 2, 3])
            score_b = random.choice([0, 1, 2, 3])
            
            score_conditions = [
                {'field': score_type_a, 'value': score_a},
                {'field': score_type_b, 'value': score_b}
            ]
            
            count = count_respondents_with_session_and_scores(case_respondents, session_name, score_conditions)
            
            question = template.format(
                session_name=session_name, score_a=score_a, score_type_a=score_type_a,
                score_b=score_b, score_type_b=score_type_b
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName', score_type_a, score_type_b],
                'filter_conditions': [{'field': 'SessionName', 'value': session_name}] + score_conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_multiple_scores',
                    'session_name': session_name,
                    'score_conditions': score_conditions,
                    'matching_count': count
                }
            }
    
    elif template_type == "total_score_threshold":
        if len(score_features) >= 2:
            score_type_a, score_type_b = random.sample(score_features, 2)
            threshold = random.choice([3, 4, 5, 6])  # Reasonable thresholds for sum of two 0-3 scores
            
            score_fields = [score_type_a, score_type_b]
            count = count_respondents_with_total_score_threshold(case_respondents, score_fields, threshold, 'greater')
            
            question = template.format(score_type_a=score_type_a, score_type_b=score_type_b, threshold=threshold)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_type_a, score_type_b],
                'filter_conditions': [{'calculated_field': 'total_score', 'threshold': threshold, 'comparison': 'greater'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'total_score_threshold',
                    'score_fields': score_fields,
                    'threshold': threshold,
                    'comparison': 'greater',
                    'matching_count': count
                }
            }
    
    else:  # score_with_keyword
        score_type = random.choice(score_features)
        score_value = random.choice([0, 1, 2, 3])
        keywords = ['Good', 'Satisfactory', 'Clear', 'Overall', 'Time', 'communication']
        keyword = random.choice(keywords)
        
        count = count_respondents_with_score_and_keyword(case_respondents, score_type, score_value, keyword)
        
        question = template.format(score=score_value, score_type=score_type, keyword=keyword)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [score_type, 'Comments'],
            'filter_conditions': [
                {'field': score_type, 'value': score_value},
                {'field': 'Comments', 'keyword': keyword}
            ],
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_with_keyword',
                'score_field': score_type,
                'score_value': score_value,
                'keyword': keyword,
                'matching_count': count
            }
        }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("above_date_average", "Count the respondents whose '{score_type}' is higher than the average '{score_type}' for all sessions on the same date."),
        ("equal_date_average", "Count the respondents whose '{score_type}' score is equal to the average '{score_type}' score for all sessions that occurred on the same date."),
        ("high_session_average", "Count the respondents who participated in a session where the average '{score_type}' for that session name is greater than {threshold}."),
        ("below_total_average", "Count the respondents whose total score across all rubric items is below the average total score for all sessions.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_date_average":
        score_type = random.choice(score_features)
        count = count_respondents_above_date_average(case_respondents, score_type)
        
        question = template.format(score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Date', score_type],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_date_average',
                'score_field': score_type,
                'matching_count': count
            }
        }
    
    elif template_type == "equal_date_average":
        score_type = random.choice(score_features)
        count = count_respondents_equal_date_average(case_respondents, score_type)
        
        question = template.format(score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Date', score_type],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'equal_date_average',
                'score_field': score_type,
                'matching_count': count
            }
        }
    
    elif template_type == "high_session_average":
        score_type = random.choice(score_features)
        threshold = random.choice([1.5, 2.0, 2.5])  # Reasonable thresholds for 0-3 scale averages
        
        count = count_respondents_in_high_average_sessions(case_respondents, score_type, threshold)
        
        question = template.format(score_type=score_type, threshold=threshold)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['SessionName', score_type],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'high_session_average',
                'score_field': score_type,
                'threshold': threshold,
                'matching_count': count
            }
        }
    
    else:  # below_total_average
        count = count_respondents_below_overall_total_average(case_respondents)
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': score_features,
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'below_total_average',
                'score_fields': score_features,
                'matching_count': count
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for isbar respondent count using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/respondent_count/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_respondent_count_qa.json"
    
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