#!/usr/bin/env python3
import json
import random
import os
import statistics

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_respondents_with_score_rule(respondents, score_field, threshold, comparison):
    """Find respondents meeting score rule."""
    matching_respondents = []
    
    for resp in respondents:
        score = resp['answers'].get(score_field)
        if score is not None:
            try:
                score_num = float(score)
                
                if comparison == 'greater' and score_num > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and score_num < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and score_num == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'between' and isinstance(threshold, tuple):
                    min_val, max_val = threshold
                    if min_val <= score_num <= max_val:
                        matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_session_and_score(respondents, session_name, score_field, threshold, comparison):
    """Find respondents from specific session meeting score rule."""
    matching_respondents = []
    
    for resp in respondents:
        resp_session = resp['answers'].get('SessionName')
        score = resp['answers'].get(score_field)
        
        if resp_session == session_name and score is not None:
            try:
                score_num = float(score)
                
                if comparison == 'equal' and score_num == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'greater' and score_num > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and score_num < threshold:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_total_score_rule(respondents, score_fields, threshold, comparison):
    """Find respondents with total score meeting rule."""
    matching_respondents = []
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in score_fields:
            score = resp['answers'].get(field)
            if score is not None:
                try:
                    total_score += float(score)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if valid_scores == len(score_fields):
            if comparison == 'greater' and total_score > threshold:
                matching_respondents.append(resp)
            elif comparison == 'less' and total_score < threshold:
                matching_respondents.append(resp)
            elif comparison == 'equal' and total_score == threshold:
                matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_with_date_and_multiple_scores(respondents, date, score_a, score_a_val, score_b, score_b_threshold, score_b_comparison):
    """Find respondents from specific date with multiple score conditions."""
    matching_respondents = []
    
    for resp in respondents:
        resp_date = resp['answers'].get('Date')
        score_a_val_resp = resp['answers'].get(score_a)
        score_b_val_resp = resp['answers'].get(score_b)
        
        if (resp_date == date and 
            score_a_val_resp is not None and 
            score_b_val_resp is not None):
            
            try:
                score_a_num = float(score_a_val_resp)
                score_b_num = float(score_b_val_resp)
                
                score_a_match = (score_a_num == score_a_val)
                
                score_b_match = False
                if score_b_comparison == 'less' and score_b_num < score_b_threshold:
                    score_b_match = True
                elif score_b_comparison == 'greater' and score_b_num > score_b_threshold:
                    score_b_match = True
                elif score_b_comparison == 'equal' and score_b_num == score_b_threshold:
                    score_b_match = True
                
                if score_a_match and score_b_match:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_equal_scores(respondents, score_a, score_b):
    """Find respondents where two scores are equal."""
    matching_respondents = []
    
    for resp in respondents:
        score_a_val = resp['answers'].get(score_a)
        score_b_val = resp['answers'].get(score_b)
        
        if score_a_val is not None and score_b_val is not None:
            try:
                if float(score_a_val) == float(score_b_val):
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def calculate_average_score_for_group(respondents, group_field, group_value, score_field):
    """Calculate average score for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    scores = []
    for resp in group_respondents:
        score = resp['answers'].get(score_field)
        if score is not None:
            try:
                scores.append(float(score))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(scores) if scores else 0

def calculate_average_total_score_for_date(respondents, date, score_fields):
    """Calculate average total score for specific date."""
    date_respondents = [r for r in respondents if r['answers'].get('Date') == date]
    
    total_scores = []
    for resp in date_respondents:
        total_score = 0
        valid_scores = 0
        
        for field in score_fields:
            score = resp['answers'].get(field)
            if score is not None:
                try:
                    total_score += float(score)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if valid_scores == len(score_fields):
            total_scores.append(total_score)
    
    return statistics.mean(total_scores) if total_scores else 0

def calculate_average_total_score_all(respondents, score_fields):
    """Calculate average total score for all respondents."""
    total_scores = []
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in score_fields:
            score = resp['answers'].get(field)
            if score is not None:
                try:
                    total_score += float(score)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if valid_scores == len(score_fields):
            total_scores.append(total_score)
    
    return statistics.mean(total_scores) if total_scores else 0

def find_respondents_above_group_average(respondents, group_field, score_field):
    """Find respondents with score above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_score = resp['answers'].get(score_field)
        
        if resp_group and resp_score is not None:
            try:
                resp_score_num = float(resp_score)
                group_avg = calculate_average_score_for_group(respondents, group_field, resp_group, score_field)
                
                if resp_score_num > group_avg:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_below_date_average(respondents, score_fields):
    """Find respondents with total score below average for their date."""
    matching_respondents = []
    
    for resp in respondents:
        resp_date = resp['answers'].get('Date')
        
        if resp_date:
            # Calculate respondent's total score
            resp_total = 0
            valid_scores = 0
            
            for field in score_fields:
                score = resp['answers'].get(field)
                if score is not None:
                    try:
                        resp_total += float(score)
                        valid_scores += 1
                    except (ValueError, TypeError):
                        pass
            
            if valid_scores == len(score_fields):
                date_avg = calculate_average_total_score_for_date(respondents, resp_date, score_fields)
                
                if resp_total < date_avg:
                    matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_above_global_average(respondents, score_fields):
    """Find respondents with total score above global average."""
    matching_respondents = []
    global_avg = calculate_average_total_score_all(respondents, score_fields)
    
    for resp in respondents:
        resp_total = 0
        valid_scores = 0
        
        for field in score_fields:
            score = resp['answers'].get(field)
            if score is not None:
                try:
                    resp_total += float(score)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        if valid_scores == len(score_fields) and resp_total > global_avg:
            matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_within_points_of_lowest(respondents, score_a, score_b, group_field, points):
    """Find respondents whose score A is within points of lowest score B in their group."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_score_a = resp['answers'].get(score_a)
        
        if resp_group and resp_score_a is not None:
            try:
                resp_score_a_num = float(resp_score_a)
                
                # Find lowest score B in the group
                group_respondents = [r for r in respondents if r['answers'].get(group_field) == resp_group]
                group_score_b_values = []
                
                for group_resp in group_respondents:
                    score_b_val = group_resp['answers'].get(score_b)
                    if score_b_val is not None:
                        try:
                            group_score_b_values.append(float(score_b_val))
                        except (ValueError, TypeError):
                            pass
                
                if group_score_b_values:
                    lowest_score_b = min(group_score_b_values)
                    
                    if abs(resp_score_a_num - lowest_score_b) <= points:
                        matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Rubric score fields (0-3 scale)
    score_fields = ['Identification', 'Situation', 'Background (history)', 'Background (examination)', 
                   'Assessment', 'Recommendation (clear recommendation)', 'Recommendation (global rating scale)']
    
    templates = [
        ("score_greater", "Which respondents scored higher than {threshold} on '{score_field}'?"),
        ("score_between", "Find all respondents whose '{score_field}' score is between {min_val} and {max_val}."),
        ("session_score_exact", "List all respondents from the '{session_name}' session whose '{score_field}' is exactly {score_value}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "score_greater":
        score_field = random.choice(score_fields)
        threshold = random.choice([1, 2])  # 0-3 scale, so threshold of 1 or 2 makes sense
        
        matching_respondents = find_respondents_with_score_rule(case_respondents, score_field, threshold, 'greater')
        
        question = template.format(threshold=threshold, score_field=score_field)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_field],
            'filter_conditions': [{'field': score_field, 'threshold': threshold, 'comparison': 'greater'}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_rule',
                'score_field': score_field,
                'threshold': threshold,
                'comparison': 'greater',
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "score_between":
        score_field = random.choice(score_fields)
        min_val = random.choice([0, 1])
        max_val = min_val + random.choice([1, 2])
        
        matching_respondents = find_respondents_with_score_rule(case_respondents, score_field, (min_val, max_val), 'between')
        
        question = template.format(score_field=score_field, min_val=min_val, max_val=max_val)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_field],
            'filter_conditions': [{'field': score_field, 'min_val': min_val, 'max_val': max_val, 'comparison': 'between'}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_range_rule',
                'score_field': score_field,
                'range': [min_val, max_val],
                'matching_count': len(matching_respondents)
            }
        }
    
    else:  # session_score_exact
        # Get available session names
        sessions = list(set([r['answers'].get('SessionName') for r in case_respondents 
                           if r['answers'].get('SessionName') is not None]))
        
        if sessions:
            session_name = random.choice(sessions)
            score_field = random.choice(score_fields)
            score_value = random.choice([0, 1, 2, 3])
            
            matching_respondents = find_respondents_with_session_and_score(
                case_respondents, session_name, score_field, score_value, 'equal'
            )
            
            question = template.format(session_name=session_name, score_field=score_field, score_value=score_value)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName', score_field],
                'filter_conditions': [
                    {'field': 'SessionName', 'value': session_name},
                    {'field': score_field, 'value': score_value, 'comparison': 'equal'}
                ],
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'session_score_exact',
                    'session_name': session_name,
                    'score_field': score_field,
                    'score_value': score_value,
                    'matching_count': len(matching_respondents)
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_fields = ['Identification', 'Situation', 'Background (history)', 'Background (examination)', 
                   'Assessment', 'Recommendation (clear recommendation)', 'Recommendation (global rating scale)']
    
    templates = [
        ("total_score", "Find all respondents whose total score for '{score_a}' and '{score_b}' is greater than {threshold}."),
        ("date_multiple_scores", "Which respondents from sessions on '{date}' have a '{score_a}' of {score_a_val} and a '{score_b}' of less than {score_b_threshold}?"),
        ("equal_scores", "List all respondents whose '{score_a}' score is equal to their '{score_b}' score.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "total_score":
        if len(score_fields) >= 2:
            score_a, score_b = random.sample(score_fields, 2)
            threshold = random.choice([3, 4, 5])  # Sum of two 0-3 scores
            
            matching_respondents = find_respondents_with_total_score_rule(
                case_respondents, [score_a, score_b], threshold, 'greater'
            )
            
            question = template.format(score_a=score_a, score_b=score_b, threshold=threshold)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'total_score', 'score_fields': [score_a, score_b], 'threshold': threshold, 'comparison': 'greater'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'total_score_rule',
                    'score_fields': [score_a, score_b],
                    'threshold': threshold,
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "date_multiple_scores":
        # Get available dates
        dates = list(set([r['answers'].get('Date') for r in case_respondents 
                         if r['answers'].get('Date') is not None]))
        
        if dates and len(score_fields) >= 2:
            date = random.choice(dates)
            score_a, score_b = random.sample(score_fields, 2)
            score_a_val = random.choice([1, 2, 3])
            score_b_threshold = random.choice([1, 2])
            
            matching_respondents = find_respondents_with_date_and_multiple_scores(
                case_respondents, date, score_a, score_a_val, score_b, score_b_threshold, 'less'
            )
            
            question = template.format(
                date=date, score_a=score_a, score_a_val=score_a_val, 
                score_b=score_b, score_b_threshold=score_b_threshold
            )
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Date', score_a, score_b],
                'filter_conditions': [
                    {'field': 'Date', 'value': date},
                    {'field': score_a, 'value': score_a_val, 'comparison': 'equal'},
                    {'field': score_b, 'threshold': score_b_threshold, 'comparison': 'less'}
                ],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'date_multiple_scores',
                    'date': date,
                    'score_a': score_a,
                    'score_a_value': score_a_val,
                    'score_b': score_b,
                    'score_b_threshold': score_b_threshold,
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # equal_scores
        if len(score_fields) >= 2:
            score_a, score_b = random.sample(score_fields, 2)
            
            matching_respondents = find_respondents_with_equal_scores(case_respondents, score_a, score_b)
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'equal_scores', 'score_fields': [score_a, score_b]}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'equal_scores',
                    'score_fields': [score_a, score_b],
                    'matching_count': len(matching_respondents)
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    score_fields = ['Identification', 'Situation', 'Background (history)', 'Background (examination)', 
                   'Assessment', 'Recommendation (clear recommendation)', 'Recommendation (global rating scale)']
    
    templates = [
        ("above_session_average", "Find all respondents whose '{score_field}' is greater than the average '{score_field}' for their session name."),
        ("below_date_average", "Which respondents have a total score across all items that is lower than the average total score for all sessions on the same date?"),
        ("within_points_lowest", "List all respondents whose '{score_a}' is within {points} point of the lowest '{score_b}' for their session name."),
        ("above_global_average", "Which respondents have a total score across all rubric items that is higher than the average total score for all respondents?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_session_average":
        score_field = random.choice(score_fields)
        
        matching_respondents = find_respondents_above_group_average(case_respondents, 'SessionName', score_field)
        
        question = template.format(score_field=score_field)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['SessionName', score_field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_session_average',
                'score_field': score_field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "below_date_average":
        matching_respondents = find_respondents_below_date_average(case_respondents, score_fields)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Date'] + score_fields,
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'below_date_average',
                'score_fields': score_fields,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "within_points_lowest":
        if len(score_fields) >= 2:
            score_a, score_b = random.sample(score_fields, 2)
            points = random.choice([1, 2])
            
            matching_respondents = find_respondents_within_points_of_lowest(
                case_respondents, score_a, score_b, 'SessionName', points
            )
            
            question = template.format(score_a=score_a, points=points, score_b=score_b)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['SessionName', score_a, score_b],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'within_points_lowest',
                    'score_a': score_a,
                    'score_b': score_b,
                    'points': points,
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # above_global_average
        matching_respondents = find_respondents_above_global_average(case_respondents, score_fields)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': score_fields,
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_global_average',
                'score_fields': score_fields,
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for isbar rule-based querying using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/isbar/rule_based_querying/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/isbar/isbar_rule_based_qa.json"
    
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