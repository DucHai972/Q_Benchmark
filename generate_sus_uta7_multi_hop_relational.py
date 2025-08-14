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
                    try:
                        value_str = str(value)
                        condition_str = str(condition_value)
                        
                        if condition_comparison == 'equal' and value_str == condition_str:
                            matching_respondents.append(resp_id)
                        elif condition_comparison == 'different' and value_str != condition_str:
                            matching_respondents.append(resp_id)
                        elif condition_comparison == 'strongly_agree' and value_str == '5':
                            matching_respondents.append(resp_id)
                    except (ValueError, TypeError):
                        pass
                break
    
    return matching_respondents

def find_respondents_with_same_feature_but_different_group(respondents, target_respondent_id, shared_feature):
    """Find respondents who share a feature with target but are in a different group."""
    # Get target's feature value and group
    target_feature_value = None
    target_group = None
    for resp in respondents:
        if resp['respondent'] == target_respondent_id:
            target_feature_value = resp['answers'].get(shared_feature)
            target_group = resp['answers'].get('Group')
            break
    
    if target_feature_value is None or target_group is None:
        return []
    
    # Find respondents with same feature but different group
    matching_respondents = []
    for resp in respondents:
        if (resp['respondent'] != target_respondent_id and 
            resp['answers'].get(shared_feature) == target_feature_value and
            resp['answers'].get('Group') != target_group):
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def calculate_average_for_group(respondents, group_code, field):
    """Calculate average of field for all respondents in specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get('Group') == group_code]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_total_positive_usability_score(respondent):
    """Calculate total positive usability score (Ease_of_Use + Integration_of_Functions) for a respondent."""
    ease_of_use = respondent['answers'].get('Ease_of_Use')
    integration = respondent['answers'].get('Integration_of_Functions')
    
    total = 0
    if ease_of_use is not None:
        try:
            total += float(ease_of_use)
        except (ValueError, TypeError):
            pass
    
    if integration is not None:
        try:
            total += float(integration)
        except (ValueError, TypeError):
            pass
    
    return total

def find_groups_with_complexity_higher_than_ease(respondents):
    """Find groups where average System_Complexity > average Ease_of_Use."""
    groups = ['A', 'B', 'C', 'D']  # Senior, Junior, Middle, Intern
    qualifying_groups = []
    
    for group in groups:
        complexity_avg = calculate_average_for_group(respondents, group, 'System_Complexity')
        ease_avg = calculate_average_for_group(respondents, group, 'Ease_of_Use')
        
        if complexity_avg > ease_avg:
            qualifying_groups.append(group)
    
    return qualifying_groups

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Usability features that can be shared
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("same_group", "Which respondents are in the same group as respondent '{target_id}'?"),
        ("same_ease_score", "Find all respondents who gave the same 'Ease_of_Use' score as respondent '{target_id}', excluding the respondent themselves."),
        ("same_usability_score", "List all respondents who rated '{feature}' the same as respondent '{target_id}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "same_group":
        feature = 'Group'
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
    
    elif template_type == "same_ease_score":
        feature = 'Ease_of_Use'
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
    
    else:  # same_usability_score
        feature = random.choice(usability_features)
        matching_respondents = find_respondents_with_same_feature(case_respondents, target_id, feature, exclude_self=True)
        
        question = template.format(target_id=target_id, feature=feature)
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
                'method': 'same_usability_score_hop',
                'target_respondent': target_id,
                'shared_feature': feature,
                'target_feature_value': target_respondent['answers'].get(feature),
                'matches_found': len(matching_respondents)
            }
        }

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_and_complexity", "Which respondents are in the same group as respondent '{target_id}' and also rated 'System_Complexity' as {score}?"),
        ("confidence_and_easy_learning", "Find all respondents who gave the same 'Confidence_in_Use' score as respondent '{target_id}' and who also strongly agree that the system is easy to learn (score of 5)."),
        ("same_score_different_group", "List all respondents who share the same '{feature}' score as respondent '{target_id}' but are not in the same group.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "group_and_complexity":
        shared_feature = 'Group'
        condition_field = 'System_Complexity'
        score = random.choice(['1', '2', '3', '4', '5'])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, score, 'equal'
        )
        
        question = template.format(target_id=target_id, score=score)
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
                'condition_score': score,
                'condition_comparison': 'equal',
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "confidence_and_easy_learning":
        shared_feature = 'Confidence_in_Use'
        condition_field = 'Ease_of_Learning'
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, '5', 'strongly_agree'
        )
        
        question = template.format(target_id=target_id)
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
                'method': 'same_feature_plus_strong_agreement',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'condition_field': condition_field,
                'condition_comparison': 'strongly_agree',
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # same_score_different_group
        feature = random.choice(usability_features)
        matching_respondents = find_respondents_with_same_feature_but_different_group(
            case_respondents, target_id, feature
        )
        
        question = template.format(target_id=target_id, feature=feature)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [feature, 'Group'],
            'target_respondent': target_id,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'same_feature_different_group',
                'target_respondent': target_id,
                'shared_feature': feature,
                'target_feature_value': target_respondent['answers'].get(feature),
                'target_group': target_respondent['answers'].get('Group'),
                'matches_found': len(matching_respondents)
            }
        }

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    usability_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 'Need_for_Technical_Support', 
                         'Integration_of_Functions', 'Inconsistency', 'Ease_of_Learning', 
                         'Cumbersome_to_Use', 'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("score_higher_than_group_avg", "Find all respondents whose '{score_type}' is higher than the average '{score_type}' for the '{group_name}' group."),
        ("group_complexity_vs_ease", "Which respondents are in a group where the average 'System_Complexity' score is higher than the average 'Ease_of_Use' score for that same group?"),
        ("positive_usability_below_group_avg", "List all respondents whose total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') is lower than the average for all respondents in the '{group_name}' group.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "score_higher_than_group_avg":
        # Choose a score type and a target group
        score_type = random.choice(usability_features)
        groups = [('A', 'Senior'), ('B', 'Junior'), ('C', 'Middle'), ('D', 'Intern')]
        group_code, group_name = random.choice(groups)
        
        # Calculate average for that group
        group_average = calculate_average_for_group(case_respondents, group_code, score_type)
        
        # Find respondents above this average
        matching_respondents = []
        for resp in case_respondents:
            score = resp['answers'].get(score_type)
            if score is not None:
                try:
                    if float(score) > group_average:
                        matching_respondents.append(resp['respondent'])
                except (ValueError, TypeError):
                    pass
        
        question = template.format(score_type=score_type, group_name=group_name)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', score_type],
            'target_respondent': None,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_above_group_average',
                'score_type': score_type,
                'target_group': {'code': group_code, 'name': group_name},
                'group_average': group_average,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "group_complexity_vs_ease":
        # Find groups where complexity average > ease average
        qualifying_groups = find_groups_with_complexity_higher_than_ease(case_respondents)
        
        # Find all respondents in these groups
        matching_respondents = []
        for resp in case_respondents:
            group = resp['answers'].get('Group')
            if group in qualifying_groups:
                matching_respondents.append(resp['respondent'])
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'System_Complexity', 'Ease_of_Use'],
            'target_respondent': None,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'group_complexity_vs_ease_comparison',
                'qualifying_groups': qualifying_groups,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "positive_usability_below_group_avg":
        # Choose a target group
        groups = [('A', 'Senior'), ('B', 'Junior'), ('C', 'Middle'), ('D', 'Intern')]
        group_code, group_name = random.choice(groups)
        
        # Calculate average positive usability score for that group
        group_respondents = [r for r in case_respondents if r['answers'].get('Group') == group_code]
        group_positive_scores = [calculate_total_positive_usability_score(r) for r in group_respondents]
        group_positive_scores = [s for s in group_positive_scores if s > 0]
        
        if group_positive_scores:
            group_avg_positive = statistics.mean(group_positive_scores)
            
            # Find respondents below this average
            matching_respondents = []
            for resp in case_respondents:
                positive_score = calculate_total_positive_usability_score(resp)
                if positive_score < group_avg_positive:
                    matching_respondents.append(resp['respondent'])
            
            question = template.format(group_name=group_name)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', 'Ease_of_Use', 'Integration_of_Functions'],
                'target_respondent': None,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'positive_usability_below_group_average',
                    'target_group': {'code': group_code, 'name': group_name},
                    'group_average_positive_score': group_avg_positive,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for sus-uta7 multi hop relational inference using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/multi_hop_relational_inference/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus_uta7_multi_hop_relational_qa.json"
    
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