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
        if part and '.' in part and part.split('.')[0].isdigit():
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part.split('.')[0]
            current_value = ['.'.join(part.split('.')[1:])] if '.' in part and len(part.split('.')) > 1 else []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(str(int(coded_answer)), str(coded_answer))

def get_nested_score(respondent, category, subcategory):
    """Get score from nested structure like Emotional Regulation Frequency."""
    category_data = respondent['answers'].get(category, {})
    if isinstance(category_data, dict):
        return category_data.get(subcategory)
    return None

def calculate_category_total(respondent, category):
    """Calculate total score for a symptom category."""
    category_data = respondent['answers'].get(category, {})
    if isinstance(category_data, dict):
        total = 0
        count = 0
        for subcategory, score in category_data.items():
            if score is not None:
                try:
                    total += float(score)
                    count += 1
                except (ValueError, TypeError):
                    pass
        return total if count > 0 else None
    return None

def find_respondents_with_score_rule(respondents, field, threshold, comparison):
    """Find respondents meeting simple score rule."""
    matching_respondents = []
    
    for resp in respondents:
        score = resp['answers'].get(field)
        if score is not None:
            try:
                score_num = float(score)
                
                if comparison == 'greater' and score_num > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'greater_equal' and score_num >= threshold:
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

def find_respondents_with_demographic_and_year(respondents, demographic_field, demographic_value, year_threshold, year_comparison):
    """Find respondents meeting demographic and year criteria."""
    matching_respondents = []
    
    for resp in respondents:
        demo_val = resp['answers'].get(demographic_field)
        birth_year = resp['answers'].get('Year of birth')
        
        if demo_val == demographic_value and birth_year is not None:
            try:
                year_num = float(birth_year)
                
                if year_comparison == 'before' and year_num < year_threshold:
                    matching_respondents.append(resp)
                elif year_comparison == 'after' and year_num > year_threshold:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_category_total_rule(respondents, category, threshold, comparison):
    """Find respondents with category total meeting rule."""
    matching_respondents = []
    
    for resp in respondents:
        total_score = calculate_category_total(resp, category)
        if total_score is not None:
            if comparison == 'greater' and total_score > threshold:
                matching_respondents.append(resp)
            elif comparison == 'less' and total_score < threshold:
                matching_respondents.append(resp)
            elif comparison == 'equal' and total_score == threshold:
                matching_respondents.append(resp)
    
    return matching_respondents

def find_respondents_with_combined_score_rule(respondents, field_a, field_b, threshold, comparison):
    """Find respondents with combined score meeting rule."""
    matching_respondents = []
    
    for resp in respondents:
        score_a = resp['answers'].get(field_a)
        score_b = resp['answers'].get(field_b)
        
        if score_a is not None and score_b is not None:
            try:
                combined_score = float(score_a) + float(score_b)
                
                if comparison == 'equal' and combined_score == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'greater' and combined_score > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and combined_score < threshold:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
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

def calculate_average_for_group(respondents, group_field, group_value, value_field):
    """Calculate average value for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        val = resp['answers'].get(value_field)
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_category_total_for_group(respondents, group_field, group_value, category):
    """Calculate average category total for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    totals = []
    for resp in group_respondents:
        total = calculate_category_total(resp, category)
        if total is not None:
            totals.append(total)
    
    return statistics.mean(totals) if totals else 0

def calculate_average_parental_education_for_socioeconomic_group(respondents, socio_status, parent_type):
    """Calculate average parental education for socioeconomic group."""
    group_respondents = [r for r in respondents if r['answers'].get('Socio-economic status') == socio_status]
    
    education_values = []
    for resp in group_respondents:
        parental_data = resp['answers'].get('Parental Education', {})
        if isinstance(parental_data, dict):
            education = parental_data.get(parent_type)
            if education is not None:
                try:
                    education_values.append(float(education))
                except (ValueError, TypeError):
                    pass
    
    return statistics.mean(education_values) if education_values else 0

def find_respondents_above_group_average(respondents, group_field, value_field):
    """Find respondents with value above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
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

def find_respondents_below_group_average(respondents, group_field, value_field):
    """Find respondents with value below their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        resp_value = resp['answers'].get(value_field)
        
        if resp_group and resp_value is not None:
            try:
                resp_num = float(resp_value)
                group_avg = calculate_average_for_group(respondents, group_field, resp_group, value_field)
                
                if resp_num < group_avg:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_category_below_birth_year_average(respondents, category):
    """Find respondents with category total below average for their birth year."""
    matching_respondents = []
    
    for resp in respondents:
        resp_year = resp['answers'].get('Year of birth')
        resp_total = calculate_category_total(resp, category)
        
        if resp_year and resp_total is not None:
            year_avg = calculate_average_category_total_for_group(respondents, 'Year of birth', resp_year, category)
            
            if resp_total < year_avg:
                matching_respondents.append(resp)
    
    return matching_respondents

def find_mothers_with_more_education_than_fathers_in_socio_group(respondents):
    """Find respondents whose mother has more education than average father in same socio group."""
    matching_respondents = []
    
    for resp in respondents:
        resp_socio = resp['answers'].get('Socio-economic status')
        parental_data = resp['answers'].get('Parental Education', {})
        
        if resp_socio and isinstance(parental_data, dict):
            mother_education = parental_data.get('Mother')
            if mother_education is not None:
                try:
                    mother_edu_num = float(mother_education)
                    fathers_avg = calculate_average_parental_education_for_socioeconomic_group(
                        respondents, resp_socio, 'Father'
                    )
                    
                    if mother_edu_num > fathers_avg:
                        matching_respondents.append(resp)
                except (ValueError, TypeError):
                    pass
    
    return matching_respondents

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Score fields (0-10 scale)
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment']
    negative_fields = ['Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    demographic_fields = ['Year of birth', 'Socio-economic status']
    
    templates = [
        ("score_greater_equal", "Which respondents have a '{field}' score of {threshold} or higher?"),
        ("demographic_between", "Find all respondents whose '{field}' is between {min_val} and {max_val}."),
        ("gender_year", "List all {gender} respondents born before {year}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "score_greater_equal":
        field = random.choice(wellbeing_fields + negative_fields)
        threshold = random.choice([6, 7, 8])  # High threshold for wellbeing, would be low for negative
        
        matching_respondents = find_respondents_with_score_rule(case_respondents, field, threshold, 'greater_equal')
        
        question = template.format(field=field, threshold=threshold)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [field],
            'filter_conditions': [{'field': field, 'threshold': threshold, 'comparison': 'greater_equal'}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_rule',
                'field': field,
                'threshold': threshold,
                'comparison': 'greater_equal',
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "demographic_between":
        field = random.choice(demographic_fields)
        
        # Get sample values to set reasonable range
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if values:
            if field == 'Year of birth':
                min_val = int(min(values))
                max_val = int(max(values))
            else:  # Socio-economic status
                min_val = int(min(values))
                max_val = min_val + 2
            
            matching_respondents = find_respondents_with_score_rule(case_respondents, field, (min_val, max_val), 'between')
            
            question = template.format(field=field, min_val=min_val, max_val=max_val)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'filter_conditions': [{'field': field, 'min_val': min_val, 'max_val': max_val, 'comparison': 'between'}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'range_rule',
                    'field': field,
                    'range': [min_val, max_val],
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # gender_year
        # Get available genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                           if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema)
            
            # Get year range
            years = [r['answers'].get('Year of birth') for r in case_respondents 
                    if r['answers'].get('Year of birth') is not None]
            
            if years:
                year_threshold = int(statistics.median(years))
                
                matching_respondents = find_respondents_with_demographic_and_year(
                    case_respondents, 'Gender', gender_code, year_threshold, 'before'
                )
                
                question = template.format(gender=gender_text.lower(), year=year_threshold)
                answer = [resp['respondent'] for resp in matching_respondents]
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Gender', 'Year of birth'],
                    'filter_conditions': [
                        {'field': 'Gender', 'value': gender_code, 'decoded_value': gender_text},
                        {'field': 'Year of birth', 'threshold': year_threshold, 'comparison': 'before'}
                    ],
                    'reasoning_complexity': 2,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'demographic_year_rule',
                        'gender': {'code': gender_code, 'text': gender_text},
                        'year_threshold': year_threshold,
                        'comparison': 'before',
                        'matching_count': len(matching_respondents)
                    }
                }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    categories = ['Emotional Regulation Frequency', 'Anxiety Symptoms Frequency', 'Depressive Symptoms Frequency']
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment']
    negative_fields = ['Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("category_total", "Find all respondents whose total score for '{category}' is greater than {threshold}."),
        ("combined_score", "Find all respondents whose combined '{field_a}' and '{field_b}' score is exactly {threshold}."),
        ("gender_year_multiple", "Which {gender} respondents born after {year} have a '{field_a}' score of {score_a} and a '{field_b}' score of less than {score_b}?"),
        ("score_comparison", "List all respondents whose '{field_a}' is greater than their '{field_b}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "category_total":
        category = random.choice(categories)
        threshold = random.choice([8, 10, 12, 15])  # Reasonable thresholds for category totals
        
        matching_respondents = find_respondents_with_category_total_rule(case_respondents, category, threshold, 'greater')
        
        question = template.format(category=category, threshold=threshold)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [category],
            'filter_conditions': [{'calculated_field': 'category_total', 'category': category, 'threshold': threshold, 'comparison': 'greater'}],
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'category_total_rule',
                'category': category,
                'threshold': threshold,
                'comparison': 'greater',
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "combined_score":
        field_a, field_b = random.sample(negative_fields, 2)
        threshold = random.choice([3, 4, 5, 6])
        
        matching_respondents = find_respondents_with_combined_score_rule(
            case_respondents, field_a, field_b, threshold, 'equal'
        )
        
        question = template.format(field_a=field_a, field_b=field_b, threshold=threshold)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [field_a, field_b],
            'filter_conditions': [{'calculated_field': 'combined_score', 'fields': [field_a, field_b], 'threshold': threshold, 'comparison': 'equal'}],
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'combined_score_rule',
                'fields': [field_a, field_b],
                'threshold': threshold,
                'comparison': 'equal',
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "gender_year_multiple":
        # Get available genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                           if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema)
            
            # Get year range
            years = [r['answers'].get('Year of birth') for r in case_respondents 
                    if r['answers'].get('Year of birth') is not None]
            
            if years:
                year_threshold = int(statistics.median(years))
                field_a = random.choice(wellbeing_fields)
                field_b = random.choice(negative_fields)
                score_a = random.choice([6, 7, 8])
                score_b = random.choice([3, 4, 5])
                
                conditions = [
                    {'field': 'Gender', 'value': gender_code, 'comparison': 'equal'},
                    {'field': 'Year of birth', 'threshold': year_threshold, 'comparison': 'greater'},
                    {'field': field_a, 'value': score_a, 'comparison': 'equal'},
                    {'field': field_b, 'threshold': score_b, 'comparison': 'less'}
                ]
                
                matching_respondents = find_respondents_with_multiple_conditions(case_respondents, conditions)
                
                question = template.format(
                    gender=gender_text.lower(), year=year_threshold, 
                    field_a=field_a, score_a=score_a, field_b=field_b, score_b=score_b
                )
                answer = [resp['respondent'] for resp in matching_respondents]
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Gender', 'Year of birth', field_a, field_b],
                    'filter_conditions': conditions,
                    'reasoning_complexity': 4,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'multiple_conditions',
                        'conditions': conditions,
                        'matching_count': len(matching_respondents)
                    }
                }
    
    else:  # score_comparison
        field_a = random.choice(wellbeing_fields)
        field_b = random.choice(negative_fields)
        
        matching_respondents = find_respondents_with_score_comparison(case_respondents, field_a, field_b, 'greater')
        
        question = template.format(field_a=field_a, field_b=field_b)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': [field_a, field_b],
            'filter_conditions': [{'calculated_field': 'score_comparison', 'field_a': field_a, 'field_b': field_b, 'comparison': 'greater'}],
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_comparison',
                'field_a': field_a,
                'field_b': field_b,
                'comparison': 'greater',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    categories = ['Emotional Regulation Frequency', 'Anxiety Symptoms Frequency', 'Depressive Symptoms Frequency']
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment']
    
    templates = [
        ("above_gender_average", "Find all respondents whose '{field}' is greater than the average '{field}' for their gender."),
        ("below_gender_average", "Which respondents have a '{field}' score that is lower than the average '{field}' score for their gender?"),
        ("category_below_year_average", "Which respondents have a total '{category}' score that is lower than the average for all respondents born in the same year?"),
        ("parental_education_comparison", "List all respondents whose mother has more years of education than the average for all fathers in the same socio-economic status group.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_gender_average":
        field = random.choice(wellbeing_fields)
        
        matching_respondents = find_respondents_above_group_average(case_respondents, 'Gender', field)
        
        question = template.format(field=field)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Gender', field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_gender_average',
                'field': field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "below_gender_average":
        field = random.choice(wellbeing_fields)
        
        matching_respondents = find_respondents_below_group_average(case_respondents, 'Gender', field)
        
        question = template.format(field=field)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Gender', field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'below_gender_average',
                'field': field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "category_below_year_average":
        category = random.choice(categories)
        
        matching_respondents = find_respondents_category_below_birth_year_average(case_respondents, category)
        
        question = template.format(category=category)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Year of birth', category],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'category_below_year_average',
                'category': category,
                'matching_count': len(matching_respondents)
            }
        }
    
    else:  # parental_education_comparison
        matching_respondents = find_mothers_with_more_education_than_fathers_in_socio_group(case_respondents)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Socio-economic status', 'Parental Education'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'parental_education_comparison',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health rule-based querying using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/rule_based_querying/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/mental_health_rule_based_qa.json"
    
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