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
                    if condition_comparison == 'equal' and value == condition_value:
                        matching_respondents.append(resp_id)
                    elif condition_comparison == 'greater':
                        try:
                            if float(value) > condition_value:
                                matching_respondents.append(resp_id)
                        except (ValueError, TypeError):
                            pass
                    elif condition_comparison == 'contains' and isinstance(value, str):
                        if condition_value.lower() in value.lower():
                            matching_respondents.append(resp_id)
                    elif condition_comparison == 'different' and value != condition_value:
                        matching_respondents.append(resp_id)
                break
    
    return matching_respondents

def calculate_average_compensation_for_education(respondents, education_level):
    """Calculate average compensation for all respondents with specific education level within this case."""
    education_respondents = [r for r in respondents if r['answers'].get('EdLevel') == education_level]
    
    values = []
    for resp in education_respondents:
        comp = resp['answers'].get('CompTotal')
        if comp is not None:
            try:
                values.append(float(comp))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_experience_for_country(respondents, country):
    """Calculate average years of coding experience for all respondents from specific country within this case."""
    country_respondents = [r for r in respondents if r['answers'].get('Country') == country]
    
    values = []
    for resp in country_respondents:
        years = resp['answers'].get('YearsCode')
        if years is not None:
            try:
                values.append(float(years))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_professional_experience_for_org_size(respondents, org_size):
    """Calculate average professional coding experience for specific organization size within this case."""
    org_respondents = [r for r in respondents if r['answers'].get('OrgSize') == org_size]
    
    values = []
    for resp in org_respondents:
        years_pro = resp['answers'].get('YearsCodePro')
        if years_pro is not None:
            try:
                values.append(float(years_pro))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Features that can be shared between developers
    shareable_features = ['MainBranch', 'Employment', 'EdLevel', 'Country', 'CompFreq', 'OrgSize', 'VersionControlSystem']
    
    templates = [
        ("same_main_branch", "Which respondents have the same 'MainBranch' (professional identity) as respondent '{target_id}'?"),
        ("same_country", "Find all respondents from the same country as respondent '{target_id}', excluding the respondent themselves."),
        ("same_education", "List all respondents who have the same education level as respondent '{target_id}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "same_main_branch":
        feature = 'MainBranch'
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
    
    elif template_type == "same_country":
        feature = 'Country'
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
    
    else:  # same_education
        feature = 'EdLevel'
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
    templates = [
        ("country_experience", "Which respondents are from the same country as respondent '{target_id}' and also have more than {years} years of coding experience?"),
        ("education_compensation", "Find all respondents who have the same education level as respondent '{target_id}' and whose total compensation is over {amount}."),
        ("main_branch_languages", "List all respondents who have the same 'MainBranch' as respondent '{target_id}' and whose programming languages include '{language}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    # Choose a random respondent as target
    if not case_respondents:
        return None
    
    target_respondent = random.choice(case_respondents)
    target_id = target_respondent['respondent']
    
    if template_type == "country_experience":
        shared_feature = 'Country'
        condition_field = 'YearsCode'
        years = random.choice([3, 5, 7, 10])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, years, 'greater'
        )
        
        question = template.format(target_id=target_id, years=years)
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
                'condition_threshold': years,
                'condition_comparison': 'greater',
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "education_compensation":
        shared_feature = 'EdLevel'
        condition_field = 'CompTotal'
        amount = random.choice([50000, 75000, 100000, 150000])
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, amount, 'greater'
        )
        
        question = template.format(target_id=target_id, amount=amount)
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
                'condition_amount': amount,
                'condition_comparison': 'greater',
                'matches_found': len(matching_respondents)
            }
        }
    
    else:  # main_branch_languages
        shared_feature = 'MainBranch'
        condition_field = 'LanguageHaveWorkedWith'
        languages = ['JavaScript', 'Python', 'Java', 'Go', 'TypeScript', 'C#', 'C++']
        language = random.choice(languages)
        
        matching_respondents = find_respondents_with_same_feature_and_condition(
            case_respondents, target_id, shared_feature, condition_field, language, 'contains'
        )
        
        question = template.format(target_id=target_id, language=language)
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
                'method': 'same_feature_plus_language',
                'target_respondent': target_id,
                'shared_feature': shared_feature,
                'condition_field': condition_field,
                'target_language': language,
                'condition_comparison': 'contains',
                'matches_found': len(matching_respondents)
            }
        }

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("compensation_above_education_avg", "Find all respondents whose total compensation is higher than the average compensation for all respondents with the same education level as respondent '{target_id}'."),
        ("experience_above_country_avg", "Which respondents have more years of coding experience than the average for all respondents from the same country?"),
        ("professional_exp_vs_org_size", "List all respondents whose professional coding experience is lower than the average professional experience for all respondents in organizations of size '{org_size}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "compensation_above_education_avg":
        # Choose a random respondent as target
        if not case_respondents:
            return None
        
        target_respondent = random.choice(case_respondents)
        target_id = target_respondent['respondent']
        target_education = target_respondent['answers'].get('EdLevel')
        
        if target_education:
            # Calculate average compensation for that education level
            education_avg_comp = calculate_average_compensation_for_education(case_respondents, target_education)
            
            # Find respondents above this average
            matching_respondents = []
            for resp in case_respondents:
                comp = resp['answers'].get('CompTotal')
                if comp is not None:
                    try:
                        if float(comp) > education_avg_comp:
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
                'selected_features': ['EdLevel', 'CompTotal'],
                'target_respondent': target_id,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'compensation_above_education_average',
                    'target_respondent': target_id,
                    'target_education': target_education,
                    'education_average_compensation': education_avg_comp,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "experience_above_country_avg":
        matching_respondents = []
        
        # Get unique countries
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        for country in countries:
            # Calculate average experience for this country
            country_avg_exp = calculate_average_experience_for_country(case_respondents, country)
            
            # Find respondents from this country with above-average experience
            country_respondents = [r for r in case_respondents if r['answers'].get('Country') == country]
            
            for resp in country_respondents:
                years_code = resp['answers'].get('YearsCode')
                if years_code is not None:
                    try:
                        if float(years_code) > country_avg_exp:
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
            'selected_features': ['Country', 'YearsCode'],
            'target_respondent': None,
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'experience_above_country_average',
                'countries_analyzed': countries,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "professional_exp_vs_org_size":
        # Choose a specific organization size that exists in the data
        org_sizes = list(set([r['answers'].get('OrgSize') for r in case_respondents 
                            if r['answers'].get('OrgSize') is not None]))
        
        if org_sizes:
            target_org_size = random.choice(org_sizes)
            
            # Calculate average professional experience for that org size
            org_avg_pro_exp = calculate_average_professional_experience_for_org_size(case_respondents, target_org_size)
            
            # Find all respondents below this average
            matching_respondents = []
            for resp in case_respondents:
                years_pro = resp['answers'].get('YearsCodePro')
                if years_pro is not None:
                    try:
                        if float(years_pro) < org_avg_pro_exp:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(org_size=target_org_size)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['OrgSize', 'YearsCodePro'],
                'target_respondent': None,
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'professional_exp_below_org_average',
                    'target_org_size': target_org_size,
                    'org_average_professional_exp': org_avg_pro_exp,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for stack-overflow-2022 multi hop relational inference using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/multi_hop_relational_inference/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stackoverflow_multi_hop_relational_qa.json"
    
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