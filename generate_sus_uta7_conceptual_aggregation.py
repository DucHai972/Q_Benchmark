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

def count_respondents_by_group(respondents, group_code):
    """Count respondents in specific group within this case."""
    count = 0
    
    for resp in respondents:
        if resp['answers'].get('Group') == group_code:
            count += 1
    
    return count

def count_respondents_by_score(respondents, score_type, score_value):
    """Count respondents with specific score within this case."""
    count = 0
    
    for resp in respondents:
        if resp['answers'].get(score_type) == str(score_value):
            count += 1
    
    return count

def count_respondents_by_combined_score(respondents, fields, threshold, comparison='less'):
    """Count respondents with combined score compared to threshold within this case."""
    count = 0
    
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
                (comparison == 'equal' and total_score == threshold) or
                (comparison == 'greater_equal' and total_score >= threshold) or
                (comparison == 'less_equal' and total_score <= threshold)):
                count += 1
    
    return count

def count_respondents_with_same_scores(respondents, score_a, score_b):
    """Count respondents who gave same score to two fields within this case."""
    count = 0
    
    for resp in respondents:
        val_a = resp['answers'].get(score_a)
        val_b = resp['answers'].get(score_b)
        
        if val_a is not None and val_b is not None and val_a == val_b:
            count += 1
    
    return count

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

def calculate_positive_usability_score(respondent):
    """Calculate total positive usability score for a respondent."""
    positive_fields = ['Ease_of_Use', 'Integration_of_Functions']
    total = 0
    
    for field in positive_fields:
        value = respondent['answers'].get(field)
        if value is not None:
            try:
                total += int(value)
            except (ValueError, TypeError):
                pass
    
    return total

def calculate_average_positive_usability_for_non_group(respondents, excluded_group):
    """Calculate average positive usability score for all respondents not in specified group within this case."""
    non_group_respondents = [r for r in respondents if r['answers'].get('Group') != excluded_group]
    
    scores = []
    for resp in non_group_respondents:
        score = calculate_positive_usability_score(resp)
        if score > 0:
            scores.append(score)
    
    return statistics.mean(scores) if scores else 0

def count_respondents_in_groups_with_complexity_vs_ease(respondents):
    """Count respondents in groups where avg System_Complexity > avg Ease_of_Use within this case."""
    groups = list(set([r['answers'].get('Group') for r in respondents 
                     if r['answers'].get('Group') is not None]))
    
    qualifying_groups = []
    for group in groups:
        complexity_avg = calculate_average_for_group(respondents, 'System_Complexity', 'Group', group)
        ease_avg = calculate_average_for_group(respondents, 'Ease_of_Use', 'Group', group)
        
        if complexity_avg > ease_avg:
            qualifying_groups.append(group)
    
    # Count respondents in qualifying groups
    count = 0
    for resp in respondents:
        if resp['answers'].get('Group') in qualifying_groups:
            count += 1
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Usability score features (Likert 1-5)
    score_features = ['Frequent_Usage', 'System_Complexity', 'Ease_of_Use', 
                     'Need_for_Technical_Support', 'Integration_of_Functions', 
                     'Inconsistency', 'Ease_of_Learning', 'Cumbersome_to_Use', 
                     'Confidence_in_Use', 'Need_to_Learn_Before_Use']
    
    templates = [
        ("group_count", "How many respondents are in the '{group}' group?"),
        ("score_count", "Count the respondents who rated '{score_type}' as {score}."),
        ("group_score_count", "How many respondents from the '{group}' rated '{score_type}' as {score}?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_count":
        # Count respondents by group only
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        if groups:
            group_code = random.choice(groups)
            group_text = decode_mcq_answer('Group', group_code, questions_schema)
            
            count = count_respondents_by_group(case_respondents, group_code)
            
            question = template.format(group=group_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Group'],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'group_count',
                    'criteria': {'Group': {'raw': group_code, 'decoded': group_text}},
                    'count': count
                }
            }
    
    elif template_type == "score_count":
        # Count respondents by score only
        score_type = random.choice(score_features)
        
        # Get possible scores for this feature within this case
        possible_scores = list(set([r['answers'].get(score_type) for r in case_respondents 
                                   if r['answers'].get(score_type) is not None]))
        
        if possible_scores:
            score = random.choice(possible_scores)
            count = count_respondents_by_score(case_respondents, score_type, score)
            
            question = template.format(score_type=score_type, score=score)
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
                    'criteria': {score_type: score},
                    'count': count
                }
            }
    
    else:  # group_score_count
        # Count respondents by group and score
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
                count = count_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(group=group_text, score_type=score_type, score=score)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Group', score_type],
                    'count': count,
                    'reasoning_complexity': 2,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'group_score_count',
                        'criteria': {
                            'Group': {'raw': group_code, 'decoded': group_text},
                            score_type: score
                        },
                        'count': count
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
        ("group_dual_scores", "How many respondents from the '{group}' group rated '{score_a}' as {score_val_a} and '{score_b}' as {score_val_b}?"),
        ("combined_score", "Count the respondents whose combined score for '{score_a}' and '{score_b}' is less than {threshold}."),
        ("same_scores", "How many respondents rated '{score_a}' and '{score_b}' with the same score?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "group_dual_scores":
        # Count respondents from specific group with two score criteria
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
                count = count_respondents_by_criteria(case_respondents, criteria)
                
                question = template.format(group=group_text, score_a=score_a, score_val_a=score_val_a,
                                         score_b=score_b, score_val_b=score_val_b)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Group', score_a, score_b],
                    'count': count,
                    'reasoning_complexity': 3,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'group_dual_scores_count',
                        'criteria': {
                            'Group': {'raw': group_code, 'decoded': group_text},
                            score_a: score_val_a,
                            score_b: score_val_b
                        },
                        'count': count
                    }
                }
    
    elif template_type == "combined_score":
        # Count respondents with combined score below threshold
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
                count = count_respondents_by_combined_score(case_respondents, [score_a, score_b], threshold, 'less')
                
                question = template.format(score_a=score_a, score_b=score_b, threshold=threshold)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': [score_a, score_b],
                    'count': count,
                    'reasoning_complexity': 4,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'combined_score_threshold_count',
                        'score_fields': [score_a, score_b],
                        'threshold': threshold,
                        'comparison': 'less',
                        'count': count
                    }
                }
    
    elif template_type == "same_scores":
        # Count respondents who gave same score to two different features
        if len(score_features) >= 2:
            score_a, score_b = random.sample(score_features, 2)
            
            count = count_respondents_with_same_scores(case_respondents, score_a, score_b)
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'same_scores_count',
                    'score_fields': [score_a, score_b],
                    'count': count
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
        ("above_other_group", "How many respondents in the '{group_a}' group have a '{score_type}' score that is higher than the average '{score_type}' for the '{group_b}' group?"),
        ("complexity_vs_ease", "Count the respondents who are in a group where the average 'System_Complexity' score is higher than the average 'Ease_of_Use' score."),
        ("positive_below_non_group", "How many respondents have a total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') that is lower than the average for all respondents not in their group?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_other_group":
        # Count respondents in one group above another group's average
        groups = list(set([r['answers'].get('Group') for r in case_respondents 
                         if r['answers'].get('Group') is not None]))
        
        if len(groups) >= 2 and score_features:
            group_a_code, group_b_code = random.sample(groups, 2)
            group_a_text = decode_mcq_answer('Group', group_a_code, questions_schema)
            group_b_text = decode_mcq_answer('Group', group_b_code, questions_schema)
            score_type = random.choice(score_features)
            
            # Calculate average for group B within this case
            group_b_average = calculate_average_for_group(case_respondents, score_type, 'Group', group_b_code)
            
            # Count respondents in group A above group B average
            count = 0
            for resp in case_respondents:
                if resp['answers'].get('Group') == group_a_code:
                    score = resp['answers'].get(score_type)
                    if score is not None:
                        try:
                            if int(score) > group_b_average:
                                count += 1
                        except (ValueError, TypeError):
                            pass
            
            question = template.format(group_a=group_a_text, score_type=score_type, group_b=group_b_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Group', score_type],
                'count': count,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_other_group_average_count',
                    'group_a': {'raw': group_a_code, 'decoded': group_a_text},
                    'group_b': {'raw': group_b_code, 'decoded': group_b_text},
                    'score_type': score_type,
                    'group_b_average': group_b_average,
                    'count': count
                }
            }
    
    elif template_type == "complexity_vs_ease":
        # Count respondents in groups where complexity > ease of use
        count = count_respondents_in_groups_with_complexity_vs_ease(case_respondents)
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'System_Complexity', 'Ease_of_Use'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'complexity_vs_ease_group_count',
                'count': count
            }
        }
    
    elif template_type == "positive_below_non_group":
        # Count respondents with positive usability below their non-group average
        count = 0
        
        # Check each respondent
        for resp in case_respondents:
            resp_group = resp['answers'].get('Group')
            resp_positive_score = calculate_positive_usability_score(resp)
            
            if resp_group and resp_positive_score > 0:
                # Calculate average for all other groups
                non_group_average = calculate_average_positive_usability_for_non_group(case_respondents, resp_group)
                
                if resp_positive_score < non_group_average:
                    count += 1
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Group', 'Ease_of_Use', 'Integration_of_Functions'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'positive_usability_below_non_group_average_count',
                'count': count
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for sus-uta7 conceptual aggregation using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/sus-uta7/conceptual_aggregation/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/sus-uta7/sus-uta7_conceptual_aggregation_qa.json"
    
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