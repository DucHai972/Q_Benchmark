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

def count_respondents_in_group(respondents, group_code):
    """Count respondents in specific group."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('Group') == group_code:
            count += 1
    return count

def count_respondents_with_score(respondents, score_field, score_value):
    """Count respondents with specific score on field."""
    count = 0
    for resp in respondents:
        score = resp['answers'].get(score_field)
        if score is not None:
            try:
                if str(score) == str(score_value):
                    count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_group_and_score(respondents, group_code, score_field, score_value):
    """Count respondents in specific group with specific score."""
    count = 0
    for resp in respondents:
        group = resp['answers'].get('Group')
        score = resp['answers'].get(score_field)
        
        if group == group_code and score is not None:
            try:
                if str(score) == str(score_value):
                    count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_multiple_scores(respondents, conditions):
    """Count respondents meeting multiple score conditions."""
    count = 0
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in conditions:
            field = condition['field']
            value = condition['value']
            comparison = condition.get('comparison', 'equal')
            
            resp_value = resp['answers'].get(field)
            if resp_value is None:
                meets_all_conditions = False
                break
            
            try:
                resp_str = str(resp_value)
                value_str = str(value)
                
                if comparison == 'equal' and resp_str != value_str:
                    meets_all_conditions = False
                    break
                elif comparison == 'less':
                    if float(resp_value) >= float(value):
                        meets_all_conditions = False
                        break
                elif comparison == 'greater':
                    if float(resp_value) <= float(value):
                        meets_all_conditions = False
                        break
            except (ValueError, TypeError):
                meets_all_conditions = False
                break
        
        if meets_all_conditions:
            count += 1
    
    return count

def count_respondents_with_combined_score_threshold(respondents, score_fields, threshold, comparison='less'):
    """Count respondents whose combined score meets threshold."""
    count = 0
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
            if comparison == 'less' and total_score < threshold:
                count += 1
            elif comparison == 'greater' and total_score > threshold:
                count += 1
            elif comparison == 'equal' and total_score == threshold:
                count += 1
    
    return count

def count_respondents_with_same_scores(respondents, score_a, score_b):
    """Count respondents who rated two fields with the same score."""
    count = 0
    for resp in respondents:
        score_a_val = resp['answers'].get(score_a)
        score_b_val = resp['answers'].get(score_b)
        
        if score_a_val is not None and score_b_val is not None:
            try:
                if str(score_a_val) == str(score_b_val):
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def calculate_average_for_group(respondents, group_code, field):
    """Calculate average score for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get('Group') == group_code]
    
    values = []
    for resp in group_respondents:
        score = resp['answers'].get(field)
        if score is not None:
            try:
                values.append(float(score))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_total_positive_usability_score(respondent):
    """Calculate total positive usability score (Ease_of_Use + Integration_of_Functions)."""
    ease = respondent['answers'].get('Ease_of_Use')
    integration = respondent['answers'].get('Integration_of_Functions')
    
    total = 0
    if ease is not None:
        try:
            total += float(ease)
        except (ValueError, TypeError):
            pass
    
    if integration is not None:
        try:
            total += float(integration)
        except (ValueError, TypeError):
            pass
    
    return total

def count_respondents_higher_than_other_group_average(respondents, target_group, comparison_group, field):
    """Count respondents in target group with field higher than comparison group's average."""
    comparison_avg = calculate_average_for_group(respondents, comparison_group, field)
    
    count = 0
    target_respondents = [r for r in respondents if r['answers'].get('Group') == target_group]
    
    for resp in target_respondents:
        score = resp['answers'].get(field)
        if score is not None:
            try:
                if float(score) > comparison_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_in_groups_complexity_vs_ease(respondents):
    """Count respondents in groups where avg System_Complexity > avg Ease_of_Use."""
    groups = ['A', 'B', 'C', 'D']  # Senior, Junior, Middle, Intern
    qualifying_groups = []
    
    for group in groups:
        complexity_avg = calculate_average_for_group(respondents, group, 'System_Complexity')
        ease_avg = calculate_average_for_group(respondents, group, 'Ease_of_Use')
        
        if complexity_avg > ease_avg:
            qualifying_groups.append(group)
    
    # Count respondents in qualifying groups
    count = 0
    for resp in respondents:
        group = resp['answers'].get('Group')
        if group in qualifying_groups:
            count += 1
    
    return count

def count_respondents_below_other_groups_positive_average(respondents):
    """Count respondents with positive usability score below average of all other groups."""
    count = 0
    
    for resp in respondents:
        resp_group = resp['answers'].get('Group')
        resp_positive_score = calculate_total_positive_usability_score(resp)
        
        if resp_group:
            # Calculate average positive score for all other groups
            other_groups_respondents = [r for r in respondents if r['answers'].get('Group') != resp_group]
            other_positive_scores = [calculate_total_positive_usability_score(r) for r in other_groups_respondents]
            other_positive_scores = [s for s in other_positive_scores if s > 0]
            
            if other_positive_scores:
                other_avg = statistics.mean(other_positive_scores)
                if resp_positive_score < other_avg:
                    count += 1
    
    return count

def count_respondents_above_own_group_average(respondents, field):
    """Count respondents with field score higher than their own group's average."""
    count = 0
    
    for resp in respondents:
        resp_group = resp['answers'].get('Group')
        resp_score = resp['answers'].get(field)
        
        if resp_group and resp_score is not None:
            try:
                resp_score_num = float(resp_score)
                group_avg = calculate_average_for_group(respondents, resp_group, field)
                
                if resp_score_num > group_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Usability score features
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group", "Count the respondents who are in the '{group_name}' group."),
        ("score", "Count the respondents who rated '{score_type}' as {score_value}."),
        ("group_and_score", "Count the respondents from the '{group_name}' group who rated '{score_type}' as {score_value}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group":
        # Get available groups
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                          if r['answers'].get('Group') is not None]))
        
        if groups:
            group_code = random.choice(groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            
            count = count_respondents_in_group(case_respondents, group_code)
            
            question = template.format(group_name=group_name)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Group'],
                'filter_conditions': [{'field': 'Group', 'value': group_code, 'decoded_value': group_name}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_filter',
                    'group': {'code': group_code, 'name': group_name},
                    'matching_count': count
                }
            }
    
    elif template_type == "score":
        score_type = random.choice(usability_features)
        score_value = random.choice([1, 2, 3, 4, 5])  # Likert scale 1-5
        
        count = count_respondents_with_score(case_respondents, score_type, score_value)
        
        question = template.format(score_type=score_type, score_value=score_value)
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
    
    else:  # group_and_score
        # Get available groups
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                          if r['answers'].get('Group') is not None]))
        
        if groups:
            group_code = random.choice(groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            score_type = random.choice(usability_features)
            score_value = random.choice([1, 2, 3, 4, 5])
            
            count = count_respondents_with_group_and_score(case_respondents, group_code, score_type, score_value)
            
            question = template.format(group_name=group_name, score_type=score_type, score_value=score_value)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_type],
                'filter_conditions': [
                    {'field': 'Group', 'value': group_code, 'decoded_value': group_name},
                    {'field': score_type, 'value': score_value}
                ],
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_and_score_filter',
                    'group': {'code': group_code, 'name': group_name},
                    'score_field': score_type,
                    'score_value': score_value,
                    'matching_count': count
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_multiple_scores", "Count the respondents from the '{group_name}' group who rated '{score_a}' as {score_a_val} and '{score_b}' as {score_b_val}."),
        ("combined_score_threshold", "Count the respondents whose combined score for '{score_a}' and '{score_b}' is less than {threshold}."),
        ("same_scores", "Count the respondents who rated '{score_a}' and '{score_b}' with the same score.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_multiple_scores":
        # Get available groups
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                          if r['answers'].get('Group') is not None]))
        
        if groups and len(usability_features) >= 2:
            group_code = random.choice(groups)
            group_name = decode_mcq_answer('Group', group_code, questions_schema)
            score_a, score_b = random.sample(usability_features, 2)
            score_a_val = random.choice([1, 2, 3, 4, 5])
            score_b_val = random.choice([1, 2, 3, 4, 5])
            
            conditions = [
                {'field': 'Group', 'value': group_code, 'comparison': 'equal'},
                {'field': score_a, 'value': score_a_val, 'comparison': 'equal'},
                {'field': score_b, 'value': score_b_val, 'comparison': 'equal'}
            ]
            
            count = count_respondents_with_multiple_scores(case_respondents, conditions)
            
            question = template.format(
                group_name=group_name, score_a=score_a, score_a_val=score_a_val,
                score_b=score_b, score_b_val=score_b_val
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_a, score_b],
                'filter_conditions': [
                    {'field': 'Group', 'value': group_code, 'decoded_value': group_name},
                    {'field': score_a, 'value': score_a_val},
                    {'field': score_b, 'value': score_b_val}
                ],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_multiple_scores',
                    'group': {'code': group_code, 'name': group_name},
                    'score_conditions': [
                        {'field': score_a, 'value': score_a_val},
                        {'field': score_b, 'value': score_b_val}
                    ],
                    'matching_count': count
                }
            }
    
    elif template_type == "combined_score_threshold":
        if len(usability_features) >= 2:
            score_a, score_b = random.sample(usability_features, 2)
            threshold = random.choice([4, 5, 6, 7, 8])  # Reasonable thresholds for sum of two 1-5 scores
            
            score_fields = [score_a, score_b]
            count = count_respondents_with_combined_score_threshold(case_respondents, score_fields, threshold, 'less')
            
            question = template.format(score_a=score_a, score_b=score_b, threshold=threshold)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'combined_score', 'score_fields': score_fields, 'threshold': threshold, 'comparison': 'less'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'combined_score_threshold',
                    'score_fields': score_fields,
                    'threshold': threshold,
                    'comparison': 'less',
                    'matching_count': count
                }
            }
    
    else:  # same_scores
        if len(usability_features) >= 2:
            score_a, score_b = random.sample(usability_features, 2)
            
            count = count_respondents_with_same_scores(case_respondents, score_a, score_b)
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'same_scores', 'score_fields': [score_a, score_b]}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'same_scores',
                    'score_fields': [score_a, score_b],
                    'matching_count': count
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_vs_other_group", "Count the respondents in the '{target_group}' group who have a '{score_type}' score that is higher than the average '{score_type}' for the '{comparison_group}' group."),
        ("complexity_vs_ease", "Count the respondents who are in a group where the average 'System_Complexity' score is higher than the average 'Ease_of_Use' score."),
        ("positive_usability_vs_others", "Count the respondents who have a total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') that is lower than the average for all respondents not in their group."),
        ("above_own_group_average", "Count the respondents who have a '{score_type}' score that is higher than the average '{score_type}' score for their group.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_vs_other_group":
        groups = ['A', 'B', 'C', 'D']  # Senior, Junior, Middle, Intern
        group_names = {'A': 'Senior', 'B': 'Junior', 'C': 'Middle', 'D': 'Intern'}
        
        if len(groups) >= 2:
            target_group, comparison_group = random.sample(groups, 2)
            target_name = group_names[target_group]
            comparison_name = group_names[comparison_group]
            score_type = random.choice(usability_features)
            
            count = count_respondents_higher_than_other_group_average(
                case_respondents, target_group, comparison_group, score_type
            )
            
            question = template.format(
                target_group=target_name, comparison_group=comparison_name, score_type=score_type
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_type],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_vs_other_group_average',
                    'target_group': {'code': target_group, 'name': target_name},
                    'comparison_group': {'code': comparison_group, 'name': comparison_name},
                    'score_field': score_type,
                    'matching_count': count
                }
            }
    
    elif template_type == "complexity_vs_ease":
        count = count_respondents_in_groups_complexity_vs_ease(case_respondents)
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'System_Complexity', 'Ease_of_Use'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'groups_complexity_vs_ease',
                'matching_count': count
            }
        }
    
    elif template_type == "positive_usability_vs_others":
        count = count_respondents_below_other_groups_positive_average(case_respondents)
        
        question = template
        answer = str(count)
        
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
                'method': 'positive_usability_vs_other_groups',
                'matching_count': count
            }
        }
    
    else:  # above_own_group_average
        score_type = random.choice(usability_features)
        count = count_respondents_above_own_group_average(case_respondents, score_type)
        
        question = template.format(score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', score_type],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_own_group_average',
                'score_field': score_type,
                'matching_count': count
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for sus-uta7 respondent count using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/respondent_count/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus_uta7_respondent_count_qa.json"
    
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