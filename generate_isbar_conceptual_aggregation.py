#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def count_respondents_by_session(respondents, session_name):
    """Count respondents who participated in a specific session within this case."""
    count = 0
    
    for resp in respondents:
        if resp['answers'].get('SessionName') == session_name:
            count += 1
    
    return count

def count_respondents_by_score(respondents, score_type, score_value):
    """Count respondents with specific score within this case."""
    count = 0
    
    for resp in respondents:
        score = resp['answers'].get(score_type)
        if score == score_value:
            count += 1
    
    return count

def count_respondents_by_date_and_score(respondents, date, score_type, score_value):
    """Count respondents from specific date with specific score within this case."""
    count = 0
    
    for resp in respondents:
        if (resp['answers'].get('Date') == date and 
            resp['answers'].get(score_type) == score_value):
            count += 1
    
    return count

def count_respondents_by_total_score(respondents, fields, threshold, comparison='greater'):
    """Count respondents with combined score compared to threshold within this case."""
    count = 0
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in fields:
            value = resp['answers'].get(field)
            if value is not None and value != -1:  # Skip missing values
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
                count += 1
    
    return count

def count_respondents_with_keyword(respondents, score_type, score_value, keyword):
    """Count respondents with specific score and keyword in comments within this case."""
    count = 0
    
    for resp in respondents:
        score = resp['answers'].get(score_type)
        comments = resp['answers'].get('Comments', '')
        
        if (score == score_value and 
            comments and isinstance(comments, str) and 
            keyword.lower() in comments.lower()):
            count += 1
    
    return count

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

def calculate_date_averages(respondents, score_field):
    """Calculate averages for each date within this case."""
    date_averages = {}
    
    # Group by date
    dates = {}
    for resp in respondents:
        date = resp['answers'].get('Date')
        if date:
            if date not in dates:
                dates[date] = []
            dates[date].append(resp)
    
    # Calculate averages
    for date, date_respondents in dates.items():
        values = []
        for resp in date_respondents:
            value = resp['answers'].get(score_field)
            if value is not None and value != -1:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass
        
        date_averages[date] = statistics.mean(values) if values else 0
    
    return date_averages

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
    score_features = ['Identification', 'Situation', 'Background (history)', 
                     'Background (examination)', 'Assessment', 
                     'Recommendation (clear recommendation)', 
                     'Recommendation (global rating scale)']
    
    templates = [
        ("session_count", "How many respondents participated in a '{session_name}' session?"),
        ("score_count", "Count the respondents who scored {score} on '{score_type}'."),
        ("date_score_count", "How many respondents from sessions on '{date}' scored {score} on '{score_type}'?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_count":
        # Count respondents in specific session
        sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                           if r['answers'].get('SessionName') is not None]))
        
        if sessions:
            session_name = random.choice(sessions)
            count = count_respondents_by_session(case_respondents, session_name)
            
            question = template.format(session_name=session_name)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName'],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_count',
                    'session_name': session_name,
                    'count': count
                }
            }
    
    elif template_type == "score_count":
        # Count respondents with specific score
        score_type = random.choice(score_features)
        
        # Get possible scores (0-3) from this case
        possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                   if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
        
        if possible_scores:
            score = random.choice(possible_scores)
            count = count_respondents_by_score(case_respondents, score_type, score)
            
            question = template.format(score=score, score_type=score_type)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [score_type],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'score_count',
                    'score_type': score_type,
                    'score_value': score,
                    'count': count
                }
            }
    
    else:  # date_score_count
        # Count respondents from specific date with specific score
        dates = list(set([r['answers'].get('Date') for r in case_respondents 
                        if r['answers'].get('Date') is not None]))
        score_type = random.choice(score_features)
        
        if dates:
            date = random.choice(dates)
            
            # Get possible scores for this date
            date_respondents = [r for r in case_respondents if r['answers'].get('Date') == date]
            possible_scores = list(set([r['answers'].get(score_type) for r in date_respondents 
                                      if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
            
            if possible_scores:
                score = random.choice(possible_scores)
                count = count_respondents_by_date_and_score(case_respondents, date, score_type, score)
                
                question = template.format(date=date, score=score, score_type=score_type)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Date', score_type],
                    'count': count,
                    'reasoning_complexity': 2,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'date_score_count',
                        'date': date,
                        'score_type': score_type,
                        'score_value': score,
                        'count': count
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
        ("session_dual_scores", "How many respondents from the '{session_name}' session scored {score_a} on '{score_type_a}' and {score_b} on '{score_type_b}'?"),
        ("total_score_threshold", "Count the respondents whose total score for '{score_type_a}' and '{score_type_b}' is greater than {threshold}."),
        ("score_with_keyword", "How many respondents who scored {score} on '{score_type}' also have 'Comments' that contain the word '{keyword}'?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "session_dual_scores":
        # Count respondents from specific session with two score criteria
        sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                           if r['answers'].get('SessionName') is not None]))
        
        if sessions and len(score_features) >= 2:
            session_name = random.choice(sessions)
            score_type_a, score_type_b = random.sample(score_features, 2)
            
            # Get session respondents
            session_respondents = [r for r in case_respondents if r['answers'].get('SessionName') == session_name]
            
            # Get possible scores for this session
            scores_a = list(set([r['answers'].get(score_type_a) for r in session_respondents 
                               if r['answers'].get(score_type_a) is not None and r['answers'].get(score_type_a) != -1]))
            scores_b = list(set([r['answers'].get(score_type_b) for r in session_respondents 
                               if r['answers'].get(score_type_b) is not None and r['answers'].get(score_type_b) != -1]))
            
            if scores_a and scores_b:
                score_a = random.choice(scores_a)
                score_b = random.choice(scores_b)
                
                criteria = {'SessionName': session_name, score_type_a: score_a, score_type_b: score_b}
                count = count_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(session_name=session_name, score_a=score_a, 
                                         score_type_a=score_type_a, score_b=score_b, score_type_b=score_type_b)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['SessionName', score_type_a, score_type_b],
                    'count': count,
                    'reasoning_complexity': 3,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'session_dual_scores_count',
                        'session_name': session_name,
                        'score_criteria': {score_type_a: score_a, score_type_b: score_b},
                        'count': count
                    }
                }
    
    elif template_type == "total_score_threshold":
        # Count respondents with total score above threshold
        if len(score_features) >= 2:
            score_type_a, score_type_b = random.sample(score_features, 2)
            
            # Calculate reasonable threshold based on scores in this case
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
                count = count_respondents_by_total_score(case_respondents, [score_type_a, score_type_b], threshold, 'greater')
                
                question = template.format(score_type_a=score_type_a, score_type_b=score_type_b, threshold=threshold)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_type_a, score_type_b],
                    'count': count,
                    'reasoning_complexity': 4,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'total_score_threshold_count',
                        'score_fields': [score_type_a, score_type_b],
                        'threshold': threshold,
                        'comparison': 'greater',
                        'count': count
                    }
                }
    
    elif template_type == "score_with_keyword":
        # Count respondents with specific score and keyword in comments
        score_type = random.choice(score_features)
        
        # Get possible scores
        possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                   if r['answers'].get(score_type) is not None and r['answers'].get(score_type) != -1]))
        
        # Common keywords in ISBAR comments
        keywords = ['Good', 'Clear', 'Satisfactory', 'Overall', 'Time', 'communication', 'unclear', 'reflected']
        
        if possible_scores:
            score = random.choice(possible_scores)
            keyword = random.choice(keywords)
            
            count = count_respondents_with_keyword(case_respondents, score_type, score, keyword)
            
            question = template.format(score=score, score_type=score_type, keyword=keyword)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_type, 'Comments'],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'score_with_keyword_count',
                    'score_type': score_type,
                    'score_value': score,
                    'keyword': keyword,
                    'count': count
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
        ("above_date_average", "How many respondents have a '{score_type}' score that is higher than the average '{score_type}' for all sessions on the same date?"),
        ("high_session_average", "Count the respondents who participated in a session where the average '{score_type}' for that session name is greater than {threshold}."),
        ("keyword_below_total_avg", "How many respondents whose comments contain '{keyword}' also have a total score across all rubric items that is below the average total score for all sessions?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_date_average":
        # Count respondents above their date's average
        score_type = random.choice(score_features)
        
        # Calculate averages by date within this case
        date_averages = calculate_date_averages(case_respondents, score_type)
        
        # Count respondents above their date average
        count = 0
        for resp in case_respondents:
            date = resp['answers'].get('Date')
            score = resp['answers'].get(score_type)
            
            if date and score is not None and score != -1 and date in date_averages:
                try:
                    if float(score) > date_averages[date]:
                        count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template.format(score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Date', score_type],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_date_average_count',
                'score_type': score_type,
                'date_averages': date_averages,
                'count': count
            }
        }
    
    elif template_type == "high_session_average":
        # Count respondents in sessions with high average
        score_type = random.choice(score_features)
        threshold = random.choice([2.0, 2.5])  # High threshold for good sessions
        
        # Calculate session averages within this case
        session_averages = calculate_session_averages(case_respondents, score_type)
        
        # Find sessions above threshold
        qualifying_sessions = [session for session, avg in session_averages.items() if avg > threshold]
        
        # Count respondents in qualifying sessions
        count = 0
        for resp in case_respondents:
            session = resp['answers'].get('SessionName')
            if session in qualifying_sessions:
                count += 1
        
        question = template.format(score_type=score_type, threshold=threshold)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['SessionName', score_type],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'high_session_average_count',
                'score_type': score_type,
                'threshold': threshold,
                'session_averages': session_averages,
                'qualifying_sessions': qualifying_sessions,
                'count': count
            }
        }
    
    elif template_type == "keyword_below_total_avg":
        # Count respondents with keyword and below average total score
        keyword = random.choice(['Good', 'Clear', 'Satisfactory', 'Overall'])
        
        # Calculate overall average total score within this case
        all_total_scores = []
        for resp in case_respondents:
            total = calculate_total_rubric_score(resp)
            if total > 0:
                all_total_scores.append(total)
        
        if all_total_scores:
            overall_average = statistics.mean(all_total_scores)
            
            # Count respondents with keyword and below average total
            count = 0
            for resp in case_respondents:
                comments = resp['answers'].get('Comments', '')
                if comments and isinstance(comments, str) and keyword.lower() in comments.lower():
                    total = calculate_total_rubric_score(resp)
                    if total < overall_average:
                        count += 1
            
            question = template.format(keyword=keyword)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Comments'] + score_features,
                'count': count,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'keyword_below_total_average_count',
                    'keyword': keyword,
                    'overall_average': overall_average,
                    'count': count
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for isbar conceptual aggregation using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/conceptual_aggregation/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_conceptual_aggregation_qa.json"
    
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