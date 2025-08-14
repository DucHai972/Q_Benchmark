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
    
    # Parse options like "1. Option1 2. Option2"
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
    
    return options.get(str(int(coded_answer)), str(coded_answer))

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
                        value_num = float(value)
                        condition_num = float(condition_value)
                        
                        if condition_comparison == 'equal' and value_num == condition_num:
                            matching_respondents.append(resp_id)
                        elif condition_comparison == 'greater' and value_num > condition_num:
                            matching_respondents.append(resp_id)
                        elif condition_comparison == 'greater_equal' and value_num >= condition_num:
                            matching_respondents.append(resp_id)
                        elif condition_comparison == 'less' and value_num < condition_num:
                            matching_respondents.append(resp_id)
                    except (ValueError, TypeError):
                        pass
                break
    
    return matching_respondents

def calculate_average_for_birth_year(respondents, birth_year, field):
    """Calculate average of field for all respondents born in specific year within this case."""
    year_respondents = [r for r in respondents if r['answers'].get('Year of birth') == birth_year]
    
    values = []
    for resp in year_respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_for_gender(respondents, gender, field):
    """Calculate average of field for all respondents of specific gender within this case."""
    gender_respondents = [r for r in respondents if r['answers'].get('Gender') == gender]
    
    values = []
    for resp in gender_respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_for_socioeconomic_status(respondents, status, field):
    """Calculate average of field for all respondents with same socio-economic status within this case."""
    status_respondents = [r for r in respondents if r['answers'].get('Socio-economic status') == status]
    
    values = []
    for resp in status_respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_total_anxiety_score(respondent):
    """Calculate total anxiety symptoms score for a respondent."""
    anxiety_fields = [
        'Anxiety Symptoms Frequency-Feeling Nervous or On Edge',
        'Anxiety Symptoms Frequency-Uncontrollable Worrying',
        'Anxiety Symptoms Frequency-Excessive Worry',
        'Anxiety Symptoms Frequency-Trouble Relaxing',
        'Anxiety Symptoms Frequency-Restlessness',
        'Anxiety Symptoms Frequency-Irritability',
        'Anxiety Symptoms Frequency-Fear Something Awful Might Happen'
    ]
    
    total = 0
    valid_scores = 0
    
    for field in anxiety_fields:
        value = respondent['answers'].get(field)
        if value is not None:
            try:
                total += float(value)
                valid_scores += 1
            except (ValueError, TypeError):
                pass
    
    return total if valid_scores > 0 else 0

def calculate_total_depressive_score(respondent):
    """Calculate total depressive symptoms score for a respondent."""
    depressive_fields = [
        'Depressive Symptoms Frequency-Anhedonia',
        'Depressive Symptoms Frequency-Depressed Mood',
        'Depressive Symptoms Frequency-Sleep Problems',
        'Depressive Symptoms Frequency-Fatigue',
        'Depressive Symptoms Frequency-Appetite Changes',
        'Depressive Symptoms Frequency-Feelings of Worthlessness',
        'Depressive Symptoms Frequency-Concentration Difficulties',
        'Depressive Symptoms Frequency-Psychomotor Changes',
        'Depressive Symptoms Frequency-Suicidal Thoughts'
    ]
    
    total = 0
    valid_scores = 0
    
    for field in depressive_fields:
        value = respondent['answers'].get(field)
        if value is not None:
            try:
                total += float(value)
                valid_scores += 1
            except (ValueError, TypeError):
                pass
    
    return total if valid_scores > 0 else 0

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Simple demographic features
    demographic_features = ['Year of birth', 'Gender', 'Socio-economic status', 'Ethnic identity']
    
    templates = [
        ("same_birth_year", "Which respondents were born in the same year as respondent '{target_id}'?"),
        ("same_gender", "Find all respondents with the same gender as respondent '{target_id}', excluding the respondent themselves."),
        ("same_socioeconomic", "List all respondents who have the same 'Socio-economic status' as respondent '{target_id}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "same_birth_year":
        feature = 'Year of birth'
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
    
    elif template_type == "same_gender":
        feature = 'Gender'
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
    
    else:  # same_socioeconomic
        feature = 'Socio-economic status'
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

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Worry', 'Depression', 'Stress', 'Loneliness']
    
    templates = [
        ("gender_satisfaction", "Which respondents are the same gender as respondent '{target_id}' and also have a 'Life satisfaction' score greater than {threshold}?"),
        ("birth_year_happiness", "Find all respondents who were born in the same year as respondent '{target_id}' and have a 'Happiness' score of {score} or more."),
        ("socioeconomic_stress", "List all respondents who have the same 'Socio-economic status' as respondent '{target_id}' and report a 'Stress' score of less than {threshold}.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "gender_satisfaction":
        shared_feature = 'Gender'
        condition_field = 'Life satisfaction'
        threshold = random.choice([5, 6, 7, 8])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, threshold, 'greater'
        )
        
        question = template.format(target_id=target_id, threshold=threshold)
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
                'condition_threshold': threshold,
                'condition_comparison': 'greater',
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "birth_year_happiness":
        shared_feature = 'Year of birth'
        condition_field = 'Happiness'
        score = random.choice([3, 4, 5, 6, 7])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, score, 'greater_equal'
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
                'condition_comparison': 'greater_equal',
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # socioeconomic_stress
        shared_feature = 'Socio-economic status'
        condition_field = 'Stress'
        threshold = random.choice([2, 3, 4, 5])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, threshold, 'less'
        )
        
        question = template.format(target_id=target_id, threshold=threshold)
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
                'condition_threshold': threshold,
                'condition_comparison': 'less',
                'matches_found': len(matching_respondents)
            }
        }

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Worry', 'Depression', 'Stress', 'Loneliness']
    
    templates = [
        ("happiness_above_year_avg", "Find all respondents whose 'Happiness' score is higher than the average 'Happiness' for all respondents born in the same year as respondent '{target_id}'."),
        ("gender_anxiety_vs_depression", "Which respondents have a total 'Anxiety Symptoms' score that is lower than the average total 'Depressive Symptoms' score for all respondents of the same gender?"),
        ("socioeconomic_father_vs_mother", "List all respondents who have more years of father's education than the average mother's education for all respondents with the same 'Socio-economic status'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "happiness_above_year_avg":
        # Choose a random respondent as target
        if not case_respondents:
            return None
        
        target_respondent = random.choice(case_respondents)
        target_id = target_respondent['respondent']
        target_birth_year = target_respondent['answers'].get('Year of birth')
        
        if target_birth_year:
            # Calculate average happiness for that birth year
            year_average = calculate_average_for_birth_year(case_respondents, target_birth_year, 'Happiness')
            
            # Find respondents above this average
            matching_respondents = []
            for resp in case_respondents:
                happiness = resp['answers'].get('Happiness')
                if happiness is not None:
                    try:
                        if float(happiness) > year_average:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(target_id=target_id)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', 'Happiness'],
                'target_respondent': target_id,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'happiness_above_year_average',
                    'target_respondent': target_id,
                    'target_birth_year': target_birth_year,
                    'year_average_happiness': year_average,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "gender_anxiety_vs_depression":
        # Find respondents whose anxiety is lower than gender's average depression
        matching_respondents = []
        
        # Get unique genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        for gender in genders:
            # Calculate average depressive score for this gender
            gender_dep_avg = calculate_average_for_gender(case_respondents, gender, None)  # We'll calculate manually
            
            # Calculate average depressive symptoms for this gender
            gender_respondents = [r for r in case_respondents if r['answers'].get('Gender') == gender]
            dep_scores = [calculate_total_depressive_score(r) for r in gender_respondents]
            dep_scores = [s for s in dep_scores if s > 0]
            
            if dep_scores:
                gender_dep_avg = statistics.mean(dep_scores)
                
                # Find respondents of this gender whose anxiety < depression average
                for resp in gender_respondents:
                    anxiety_score = calculate_total_anxiety_score(resp)
                    if anxiety_score < gender_dep_avg:
                        matching_respondents.append(resp['respondent'])
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Gender', 'Anxiety Symptoms', 'Depressive Symptoms'],
            'target_respondent': None,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'gender_anxiety_vs_depression_average',
                'genders_analyzed': genders,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "socioeconomic_father_vs_mother":
        # Find respondents whose father education > average mother education for their socioeconomic status
        matching_respondents = []
        
        # Get unique socioeconomic statuses
        statuses = list(set([r['answers'].get('Socio-economic status') for r in case_respondents 
                           if r['answers'].get('Socio-economic status') is not None]))
        
        for status in statuses:
            # Calculate average mother education for this status
            mother_avg = calculate_average_for_socioeconomic_status(case_respondents, status, 'Parental Education-Mother')
            
            # Find respondents of this status whose father education > mother average
            status_respondents = [r for r in case_respondents if r['answers'].get('Socio-economic status') == status]
            
            for resp in status_respondents:
                father_edu = resp['answers'].get('Parental Education-Father')
                if father_edu is not None:
                    try:
                        if float(father_edu) > mother_avg:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Socio-economic status', 'Parental Education-Father', 'Parental Education-Mother'],
            'target_respondent': None,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'socioeconomic_father_vs_mother_average',
                'statuses_analyzed': statuses,
                'matches_found': len(matching_respondents)
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health multi hop relational inference using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/multi_hop_relational_inference/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/mental_health_multi_hop_relational_qa.json"
    
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