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

def find_respondents_by_group(respondents, group_code):
    """Find all respondents in a specific group within this case."""
    matching_respondents = []
    
    for resp in respondents:
        if resp['answers'].get('Group') == group_code:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_score(respondents, score_type, score_value):
    """Find all respondents with specific score within this case."""
    matching_respondents = []
    
    for resp in respondents:
        if resp['answers'].get(score_type) == str(score_value):
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_combined_score(respondents, fields, threshold, comparison='less'):
    """Find all respondents with combined score compared to threshold within this case."""
    matching_respondents = []
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in fields:
            value = resp['answers'].get(field)
            if value is not None:
                try:
                    total_score += int(value)
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

def find_respondents_with_same_scores(respondents, score_a, score_b):
    """Find all respondents who gave the same score to two fields within this case."""
    matching_respondents = []
    
    for resp in respondents:
        val_a = resp['answers'].get(score_a)
        val_b = resp['answers'].get(score_b)
        
        if val_a is not None and val_b is not None and val_a == val_b:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def calculate_average_for_group(respondents, target_field, group_field, group_value):
    """Calculate average of target_field for respondents in specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(target_field)
        if value is not None:
            try:
                values.append(int(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_negative_usability_score(respondent):
    """Calculate total negative usability score for a respondent."""
    negative_fields = ['System_Complexity', 'Inconsistency', 'Cumbersome_to_Use']
    total = 0
    
    for field in negative_fields:
        value = respondent['answers'].get(field)
        if value is not None:
            try:
                total += int(value)
            except (ValueError, TypeError):
                pass
    
    return total

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Usability score features (Likert 1-5)
    score_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 
                     'Need_for_Technical_Support', 'Integration_of_Functions', 
                     'Inconsistency', 'Ease_of_Learning', 'Cumbersome_to_Use', 
                     'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_only", "Which respondents are in the '{group}' group?"),
        ("score_only", "Find all respondents who rated '{score_type}' as {score}."),
        ("group_score", "List all respondents from the '{group}' group who rated '{score_type}' as {score}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_only":
        # Find respondents by group only
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        if groups:
            group_code = random.choice(groups)
            group_text = decode_mcq_answer('Group', group_code, questions_schema)
            
            matching_respondents = find_respondents_by_group(case_respondents, group_code)
            
            question = template.format(group=group_text)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Group'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Group'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_filter',
                    'criteria': {'Group': {'raw': group_code, 'decoded': group_text}},
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "score_only":
        # Find respondents by score only
        score_type = random.choice(score_features)
        
        # Get possible scores for this feature within this case
        possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                   if r['answers'].get(score_type) is not None]))
        
        if possible_scores:
            score = random.choice(possible_scores)
            matching_respondents = find_respondents_by_score(case_respondents, score_type, score)
            
            question = template.format(score_type=score_type, score=score)
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
    
    else:  # group_score
        # Find respondents by group and score
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        score_type = random.choice(score_features)
        
        if groups:
            group_code = random.choice(groups)
            group_text = decode_mcq_answer('Group', group_code, questions_schema)
            
            # Get possible scores for this group within this case
            group_respondents = [r for r in case_respondents if r['answers'].get('Group') == group_code]
            possible_scores = list(set([r['answers'].get(score_type) for r in group_respondents 
                                      if r['answers'].get(score_type) is not None]))
            
            if possible_scores:
                score = random.choice(possible_scores)
                
                criteria = {'Group': group_code, score_type: score}
                matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(group=group_text, score_type=score_type, score=score)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Group', score_type])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Group', score_type],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'group_score_filter',
                        'criteria': {
                            'Group': {'raw': group_code, 'decoded': group_text},
                            score_type: score
                        },
                        'matches_found': len(matching_respondents)
                    }
                }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    score_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 
                     'Need_for_Technical_Support', 'Integration_of_Functions', 
                     'Inconsistency', 'Ease_of_Learning', 'Cumbersome_to_Use', 
                     'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_dual_scores", "Which respondents from the '{group}' group rated '{score_a}' as {score_val_a} and '{score_b}' as {score_val_b}?"),
        ("combined_score", "Find all respondents whose combined score for '{score_a}' and '{score_b}' is less than {threshold}."),
        ("same_scores", "List all respondents who rated '{score_a}' and '{score_b}' with the same score.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_dual_scores":
        # Find respondents from specific group with two score criteria
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        if groups and len(score_features) >= 2:
            group_code = random.choice(groups)
            group_text = decode_mcq_answer('Group', group_code, questions_schema)
            score_a, score_b = random.sample(score_features, 2)
            
            # Get possible scores for this group within this case
            group_respondents = [r for r in case_respondents if r['answers'].get('Group') == group_code]
            
            scores_a = list(set([r['answers'].get(score_a) for r in group_respondents 
                               if r['answers'].get(score_a) is not None]))
            scores_b = list(set([r['answers'].get(score_b) for r in group_respondents 
                               if r['answers'].get(score_b) is not None]))
            
            if scores_a and scores_b:
                score_val_a = random.choice(scores_a)
                score_val_b = random.choice(scores_b)
                
                criteria = {'Group': group_code, score_a: score_val_a, score_b: score_val_b}
                matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(group=group_text, score_a=score_a, score_val_a=score_val_a,
                                         score_b=score_b, score_val_b=score_val_b)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Group', score_a, score_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Group', score_a, score_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'group_dual_scores_filter',
                        'criteria': {
                            'Group': {'raw': group_code, 'decoded': group_text},
                            score_a: score_val_a,
                            score_b: score_val_b
                        },
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "combined_score":
        # Find respondents with combined score below threshold
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            
            # Calculate reasonable threshold based on available scores within this case
            combined_scores = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_a)
                val_b = resp['answers'].get(score_b)
                if val_a is not None and val_b is not None:
                    try:
                        combined = int(val_a) + int(val_b)
                        combined_scores.append(combined)
                    except (ValueError, TypeError):
                        pass
            
            if combined_scores:
                threshold = int(statistics.median(combined_scores))
                matching_respondents = find_respondents_by_combined_score(case_respondents, [score_a, score_b], threshold, 'less')
                
                question = template.format(score_a=score_a, score_b=score_b, threshold=threshold)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, [score_a, score_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_a, score_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 4,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'combined_score_threshold',
                        'score_fields': [score_a, score_b],
                        'threshold': threshold,
                        'comparison': 'less',
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "same_scores":
        # Find respondents who gave same score to two different features
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            
            matching_respondents = find_respondents_with_same_scores(case_respondents, score_a, score_b)
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [score_a, score_b])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 3,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'same_scores_filter',
                    'score_fields': [score_a, score_b],
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    score_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 
                     'Need_for_Technical_Support', 'Integration_of_Functions', 
                     'Inconsistency', 'Ease_of_Learning', 'Cumbersome_to_Use', 
                     'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("above_other_group", "Find all respondents in the '{group_a}' group whose '{score_type}' is higher than the average '{score_type}' for the '{group_b}' group."),
        ("negative_above_group_avg", "Which respondents have a total negative usability score ('System_Complexity' + 'Inconsistency' + 'Cumbersome_to_Use') that is higher than the average for their group?"),
        ("above_own_group_avg", "Find all respondents whose '{score_type}' score is higher than the average '{score_type}' score for their group.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_other_group":
        # Find respondents in one group above another group's average
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        if len(groups) >= 2 and score_features:
            group_a_code, group_b_code = random.sample(groups, 2)
            group_a_text = decode_mcq_answer('Group', group_a_code, questions_schema)
            group_b_text = decode_mcq_answer('Group', group_b_code, questions_schema)
            score_type = random.choice(score_features)
            
            # Calculate average for group B within this case
            group_b_average = calculate_average_for_group(case_respondents, score_type, 'Group', group_b_code)
            
            # Find respondents in group A above group B average
            matching_respondents = []
            for resp in case_respondents:
                if resp['answers'].get('Group') == group_a_code:
                    score = resp['answers'].get(score_type)
                    if score is not None:
                        try:
                            if int(score) > group_b_average:
                                matching_respondents.append(resp['respondent'])
                        except (ValueError, TypeError):
                            pass
            
            question = template.format(group_a=group_a_text, score_type=score_type, group_b=group_b_text)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Group', score_type])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_type],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_other_group_average',
                    'group_a': {'raw': group_a_code, 'decoded': group_a_text},
                    'group_b': {'raw': group_b_code, 'decoded': group_b_text},
                    'score_type': score_type,
                    'group_b_average': group_b_average,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "negative_above_group_avg":
        # Find respondents with negative usability score above their group average
        matching_respondents = []
        
        # Calculate averages by group within this case
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        group_averages = {}
        for group in groups:
            group_respondents = [r for r in case_respondents if r['answers'].get('Group') == group]
            group_scores = []
            for resp in group_respondents:
                score = calculate_negative_usability_score(resp)
                group_scores.append(score)
            
            if group_scores:
                group_averages[group] = statistics.mean(group_scores)
            else:
                group_averages[group] = 0
        
        # Find respondents above their group average
        for resp in case_respondents:
            group = resp['answers'].get('Group')
            if group and group in group_averages:
                score = calculate_negative_usability_score(resp)
                if score > group_averages[group]:
                    matching_respondents.append(resp['respondent'])
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        feature_values = extract_feature_values(case_respondents, ['Group', 'System_Complexity', 'Inconsistency', 'Cumbersome_to_Use'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'System_Complexity', 'Inconsistency', 'Cumbersome_to_Use'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'negative_usability_above_group_average',
                'group_averages': {decode_mcq_answer('Group', k, questions_schema): v for k, v in group_averages.items()},
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "above_own_group_avg":
        # Find respondents above their own group average for a score
        if score_features:
            score_type = random.choice(score_features)
            matching_respondents = []
            
            # Calculate averages by group within this case
            groups = list(set([r['answers'].get('Group') for r in case_respondents 
                             if r['answers'].get('Group') is not None]))
            
            group_averages = {}
            for group in groups:
                group_average = calculate_average_for_group(case_respondents, score_type, 'Group', group)
                group_averages[group] = group_average
            
            # Find respondents above their group average
            for resp in case_respondents:
                group = resp['answers'].get('Group')
                score = resp['answers'].get(score_type)
                
                if group and score is not None and group in group_averages:
                    try:
                        if int(score) > group_averages[group]:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(score_type=score_type)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Group', score_type])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_type],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_own_group_average',
                    'score_type': score_type,
                    'group_averages': {decode_mcq_answer('Group', k, questions_schema): v for k, v in group_averages.items()},
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for sus-uta7 answer reverse lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/answer_reverse_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus-uta7_answer_reverse_lookup_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names from the questions schema
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