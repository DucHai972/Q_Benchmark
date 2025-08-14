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

def find_respondents_with_group_and_score(respondents, group_code, score_field, threshold, comparison):
    """Find respondents from specific group meeting score rule."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get('Group')
        score = resp['answers'].get(score_field)
        
        if resp_group == group_code and score is not None:
            try:
                score_num = float(score)
                
                if comparison == 'equal' and score_num == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'greater' and score_num > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and score_num < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'greater_equal' and score_num >= threshold:
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

def find_respondents_with_multiple_conditions(respondents, conditions):
    """Find respondents meeting multiple conditions."""
    matching_respondents = []
    
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in conditions:
            field = condition['field']
            value = condition.get('value')
            threshold = condition.get('threshold')
            comparison = condition.get('comparison', 'equal')
            
            resp_value = resp['answers'].get(field)
            
            if comparison == 'equal':
                if resp_value != value:
                    meets_all_conditions = False
                    break
            elif comparison in ['greater', 'less', 'greater_equal']:
                if resp_value is None:
                    meets_all_conditions = False
                    break
                try:
                    resp_num = float(resp_value)
                    thresh_num = float(threshold)
                    
                    if comparison == 'greater' and resp_num <= thresh_num:
                        meets_all_conditions = False
                        break
                    elif comparison == 'greater_equal' and resp_num < thresh_num:
                        meets_all_conditions = False
                        break
                    elif comparison == 'less' and resp_num >= thresh_num:
                        meets_all_conditions = False
                        break
                except (ValueError, TypeError):
                    meets_all_conditions = False
                    break
        
        if meets_all_conditions:
            matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_with_score_comparison(respondents, field_a, field_b, comparison):
    """Find respondents where field A comparison field B."""
    matching_respondents = []
    
    for resp in respondents:
        score_a = resp['answers'].get(field_a)
        score_b = resp['answers'].get(field_b)
        
        if score_a is not None and score_b is not None:
            try:
                score_a_num = float(score_a)
                score_b_num = float(score_b)
                
                if comparison == 'greater' and score_a_num > score_b_num:
                    matching_respondents.append(resp)
                elif comparison == 'less' and score_a_num < score_b_num:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and score_a_num == score_b_num:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def calculate_positive_usability_score(respondent):
    """Calculate positive usability score (Ease_of_Use + Integration_of_Functions)."""
    ease = respondent['answers'].get('Ease_of_Use')
    integration = respondent['answers'].get('Integration_of_Functions')
    
    total = 0
    if ease is not None and integration is not None:
        try:
            total = float(ease) + float(integration)
        except (ValueError, TypeError):
            return None
    else:
        return None
    
    return total

def calculate_average_for_group(respondents, group_field, group_value, value_field):
    """Calculate average value for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        if value_field == 'positive_usability_score':
            val = calculate_positive_usability_score(resp)
        else:
            val = resp['answers'].get(value_field)
        
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def find_highest_score_in_group(respondents, group_field, group_value, score_field):
    """Find highest score for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    scores = []
    for resp in group_respondents:
        score = resp['answers'].get(score_field)
        if score is not None:
            try:
                scores.append(float(score))
            except (ValueError, TypeError):
                pass
    
    return max(scores) if scores else 0

def find_respondents_above_group_average(respondents, group_field, value_field):
    """Find respondents with value above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        
        if value_field == 'positive_usability_score':
            resp_value = calculate_positive_usability_score(resp)
        else:
            resp_value = resp['answers'].get(value_field)
        
        if resp_group and resp_value is not None:
            try:
                resp_num = float(resp_value)
                group_avg = calculate_average_for_group(respondents, group_field, resp_group, value_field)
                
                if resp_num > group_avg:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_below_other_groups_average(respondents):
    """Find respondents with positive usability score below average of other groups."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get('Group')
        resp_positive_score = calculate_positive_usability_score(resp)
        
        if resp_group and resp_positive_score is not None:
            # Calculate average positive score for all other groups
            other_groups_respondents = [r for r in respondents if r['answers'].get('Group') != resp_group]
            other_positive_scores = []
            
            for other_resp in other_groups_respondents:
                other_score = calculate_positive_usability_score(other_resp)
                if other_score is not None:
                    other_positive_scores.append(other_score)
            
            if other_positive_scores:
                other_avg = statistics.mean(other_positive_scores)
                if resp_positive_score < other_avg:
                    matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_within_points_of_highest(respondents, score_a, score_b, group_field, points):
    """Find respondents whose score A is within points of highest score B in their group."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_score_a = resp['answers'].get(score_a)
        
        if resp_group and resp_score_a is not None:
            try:
                resp_score_a_num = float(resp_score_a)
                
                # Find highest score B in the group
                highest_score_b = find_highest_score_in_group(respondents, group_field, resp_group, score_b)
                
                if abs(resp_score_a_num - highest_score_b) <= points:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Usability score fields (1-5 scale)
    usability_fields = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                       'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                       'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("score_greater", "Which respondents scored higher than {threshold} on '{score_field}'?"),
        ("score_between", "Find all respondents whose '{score_field}' score is between {min_val} and {max_val}."),
        ("group_score_exact", "List all respondents from the '{group_name}' group whose '{score_field}' is exactly {score_value}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "score_greater":
        score_field = random.choice(usability_fields)
        threshold = random.choice([2, 3])  # 1-5 scale, so threshold of 2 or 3 makes sense
        
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
        score_field = random.choice(usability_fields)
        min_val = random.choice([1, 2])
        max_val = min_val + random.choice([1, 2, 3])
        
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
    
    else:  # group_score_exact
        # Get available groups
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                          if r['answers'].get('Group') is not None]))
        
        if groups:
            group_code = random.choice(groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            score_field = random.choice(usability_fields)
            score_value = random.choice([1, 2, 3, 4, 5])
            
            matching_respondents = find_respondents_with_group_and_score(
                case_respondents, group_code, score_field, score_value, 'equal'
            )
            
            question = template.format(group_name=group_name, score_field=score_field, score_value=score_value)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_field],
                'filter_conditions': [
                    {'field': 'Group', 'value': group_code, 'decoded_value': group_name},
                    {'field': score_field, 'value': score_value, 'comparison': 'equal'}
                ],
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_score_exact',
                    'group': {'code': group_code, 'name': group_name},
                    'score_field': score_field,
                    'score_value': score_value,
                    'matching_count': len(matching_respondents)
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    usability_fields = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                       'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                       'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("total_score", "Find all respondents whose total score for '{score_a}' and '{score_b}' is less than {threshold}."),
        ("group_multiple_scores", "Which respondents from the '{group_name}' group have a '{score_a}' of {score_a_val} or more and a '{score_b}' of less than {score_b_val}?"),
        ("score_comparison", "List all respondents whose '{score_a}' score is greater than their '{score_b}' score.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "total_score":
        if len(usability_fields) >= 2:
            score_a, score_b = random.sample(usability_fields, 2)
            threshold = random.choice([4, 5, 6, 7])  # Sum of two 1-5 scores
            
            matching_respondents = find_respondents_with_total_score_rule(
                case_respondents, [score_a, score_b], threshold, 'less'
            )
            
            question = template.format(score_a=score_a, score_b=score_b, threshold=threshold)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'total_score', 'score_fields': [score_a, score_b], 'threshold': threshold, 'comparison': 'less'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'total_score_rule',
                    'score_fields': [score_a, score_b],
                    'threshold': threshold,
                    'comparison': 'less',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "group_multiple_scores":
        # Get available groups
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                          if r['answers'].get('Group') is not None]))
        
        if groups and len(usability_fields) >= 2:
            group_code = random.choice(groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            score_a, score_b = random.sample(usability_fields, 2)
            score_a_val = random.choice([3, 4])
            score_b_val = random.choice([3, 4])
            
            conditions = [
                {'field': 'Group', 'value': group_code, 'comparison': 'equal'},
                {'field': score_a, 'threshold': score_a_val, 'comparison': 'greater_equal'},
                {'field': score_b, 'threshold': score_b_val, 'comparison': 'less'}
            ]
            
            matching_respondents = find_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(
                group_name=group_name, score_a=score_a, score_a_val=score_a_val,
                score_b=score_b, score_b_val=score_b_val
            )
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_a, score_b],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_multiple_scores',
                    'group': {'code': group_code, 'name': group_name},
                    'score_conditions': [
                        {'field': score_a, 'threshold': score_a_val, 'comparison': 'greater_equal'},
                        {'field': score_b, 'threshold': score_b_val, 'comparison': 'less'}
                    ],
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # score_comparison
        if len(usability_fields) >= 2:
            score_a, score_b = random.sample(usability_fields, 2)
            
            matching_respondents = find_respondents_with_score_comparison(case_respondents, score_a, score_b, 'greater')
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'score_comparison', 'score_fields': [score_a, score_b], 'comparison': 'greater'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'score_comparison',
                    'score_fields': [score_a, score_b],
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    usability_fields = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                       'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                       'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("above_group_average", "Find all respondents whose '{score_field}' is greater than the average '{score_field}' for their group."),
        ("positive_usability_below_others", "Which respondents have a total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') that is lower than the average for all respondents in a different group?"),
        ("within_points_highest", "List all respondents whose '{score_a}' is within {points} point of the highest '{score_b}' for their group."),
        ("ease_above_group_average", "Which respondents have an 'Ease_of_Use' score that is higher than the average 'Ease_of_Use' score for their group?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_group_average":
        score_field = random.choice(usability_fields)
        
        matching_respondents = find_respondents_above_group_average(case_respondents, 'Group', score_field)
        
        question = template.format(score_field=score_field)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', score_field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_group_average',
                'score_field': score_field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "positive_usability_below_others":
        matching_respondents = find_respondents_below_other_groups_average(case_respondents)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'Ease_of_Use', 'Integration_of_Functions'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'positive_usability_below_other_groups',
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "within_points_highest":
        if len(usability_fields) >= 2:
            score_a, score_b = random.sample(usability_fields, 2)
            points = random.choice([1, 2])
            
            matching_respondents = find_respondents_within_points_of_highest(
                case_respondents, score_a, score_b, 'Group', points
            )
            
            question = template.format(score_a=score_a, points=points, score_b=score_b)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_a, score_b],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'within_points_highest',
                    'score_a': score_a,
                    'score_b': score_b,
                    'points': points,
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # ease_above_group_average
        matching_respondents = find_respondents_above_group_average(case_respondents, 'Group', 'Ease_of_Use')
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'Ease_of_Use'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'ease_above_group_average',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for sus-uta7 rule-based querying using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/rule_based_querying/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus_uta7_rule_based_qa.json"
    
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