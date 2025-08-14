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

def count_respondents_with_gender(respondents, gender_code):
    """Count respondents with specific gender."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('Gender') == gender_code:
            count += 1
    return count

def count_respondents_with_birth_year_filter(respondents, year, comparison='before'):
    """Count respondents with birth year filter."""
    count = 0
    for resp in respondents:
        birth_year = resp['answers'].get('Year of birth')
        if birth_year is not None:
            try:
                birth_year_num = float(birth_year)
                if comparison == 'before' and birth_year_num < year:
                    count += 1
                elif comparison == 'after' and birth_year_num > year:
                    count += 1
                elif comparison == 'equal' and birth_year_num == year:
                    count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_score_threshold(respondents, score_field, threshold, comparison='greater_equal'):
    """Count respondents with score meeting threshold."""
    count = 0
    for resp in respondents:
        score = resp['answers'].get(score_field)
        if score is not None:
            try:
                score_num = float(score)
                if comparison == 'greater_equal' and score_num >= threshold:
                    count += 1
                elif comparison == 'greater' and score_num > threshold:
                    count += 1
                elif comparison == 'less_equal' and score_num <= threshold:
                    count += 1
                elif comparison == 'less' and score_num < threshold:
                    count += 1
                elif comparison == 'equal' and score_num == threshold:
                    count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_multiple_conditions(respondents, conditions):
    """Count respondents meeting multiple conditions."""
    count = 0
    for resp in respondents:
        meets_all_conditions = True
        
        for condition in conditions:
            field = condition['field']
            value = condition.get('value')
            threshold = condition.get('threshold')
            comparison = condition.get('comparison', 'equal')
            
            resp_value = resp['answers'].get(field)
            if resp_value is None:
                meets_all_conditions = False
                break
            
            try:
                if comparison == 'equal':
                    if resp_value != value:
                        meets_all_conditions = False
                        break
                elif comparison in ['greater', 'greater_equal', 'less', 'less_equal']:
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
                    elif comparison == 'less_equal' and resp_num > thresh_num:
                        meets_all_conditions = False
                        break
            except (ValueError, TypeError):
                meets_all_conditions = False
                break
        
        if meets_all_conditions:
            count += 1
    
    return count

def count_respondents_with_total_score(respondents, score_fields, target_total):
    """Count respondents whose total score across fields equals target."""
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
        
        if valid_scores == len(score_fields) and total_score == target_total:
            count += 1
    
    return count

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
        score = respondent['answers'].get(field)
        if score is not None:
            try:
                total += float(score)
                valid_scores += 1
            except (ValueError, TypeError):
                pass
    
    return total if valid_scores > 0 else 0

def calculate_average_for_gender(respondents, gender_code, field):
    """Calculate average of field for specific gender."""
    gender_respondents = [r for r in respondents if r['answers'].get('Gender') == gender_code]
    
    values = []
    for resp in gender_respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_for_birth_year(respondents, birth_year, field):
    """Calculate average of field for specific birth year."""
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

def calculate_average_for_socioeconomic_status(respondents, status, field):
    """Calculate average of field for specific socio-economic status."""
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

def count_respondents_above_gender_average(respondents, field):
    """Count respondents with field value above their gender's average."""
    count = 0
    
    # Get unique genders
    genders = list(set([r['answers'].get('Gender') for r in respondents 
                       if r['answers'].get('Gender') is not None]))
    
    for resp in respondents:
        resp_gender = resp['answers'].get('Gender')
        resp_value = resp['answers'].get(field)
        
        if resp_gender and resp_value is not None:
            try:
                resp_value_num = float(resp_value)
                gender_avg = calculate_average_for_gender(respondents, resp_gender, field)
                
                if resp_value_num > gender_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_above_socioeconomic_average(respondents, field):
    """Count respondents with field value above their socio-economic status group's average."""
    count = 0
    
    for resp in respondents:
        resp_status = resp['answers'].get('Socio-economic status')
        resp_value = resp['answers'].get(field)
        
        if resp_status and resp_value is not None:
            try:
                resp_value_num = float(resp_value)
                status_avg = calculate_average_for_socioeconomic_status(respondents, resp_status, field)
                
                if resp_value_num > status_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_below_gender_combined_average(respondents, field_a, field_b):
    """Count respondents whose combined score is below their gender's average combined score."""
    count = 0
    
    for resp in respondents:
        resp_gender = resp['answers'].get('Gender')
        score_a = resp['answers'].get(field_a)
        score_b = resp['answers'].get(field_b)
        
        if resp_gender and score_a is not None and score_b is not None:
            try:
                resp_combined = float(score_a) + float(score_b)
                
                # Calculate gender average for combined score
                gender_respondents = [r for r in respondents if r['answers'].get('Gender') == resp_gender]
                gender_combined_scores = []
                
                for gender_resp in gender_respondents:
                    g_score_a = gender_resp['answers'].get(field_a)
                    g_score_b = gender_resp['answers'].get(field_b)
                    if g_score_a is not None and g_score_b is not None:
                        try:
                            gender_combined_scores.append(float(g_score_a) + float(g_score_b))
                        except (ValueError, TypeError):
                            pass
                
                if gender_combined_scores:
                    gender_avg_combined = statistics.mean(gender_combined_scores)
                    if resp_combined < gender_avg_combined:
                        count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Basic demographic and wellbeing features
    demographic_fields = ['Gender', 'Year of birth', 'Socio-economic status']
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Worry', 'Depression', 'Stress', 'Loneliness']
    
    templates = [
        ("gender", "Count the respondents who are {gender}."),
        ("birth_year", "Count the respondents born {comparison} {year}."),
        ("score_threshold", "Count the respondents with a '{score_type}' of {threshold} or {direction}."),
        ("two_conditions", "Count the respondents with a 'Socio-economic status' of {status} who were born in {year}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "gender":
        # Get available genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                           if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema)
            
            count = count_respondents_with_gender(case_respondents, gender_code)
            
            question = template.format(gender=gender_text.lower())
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender'],
                'filter_conditions': [{'field': 'Gender', 'value': gender_code, 'decoded_value': gender_text}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'gender_filter',
                    'gender': {'code': gender_code, 'text': gender_text},
                    'matching_count': count
                }
            }
    
    elif template_type == "birth_year":
        comparison_type = random.choice(['before', 'after'])
        year = random.choice([2000, 2001, 2002, 2003, 2004, 2005])
        
        count = count_respondents_with_birth_year_filter(case_respondents, year, comparison_type)
        
        question = template.format(comparison=comparison_type, year=year)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': ['Year of birth'],
            'filter_conditions': [{'field': 'Year of birth', 'year': year, 'comparison': comparison_type}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'birth_year_filter',
                'year': year,
                'comparison': comparison_type,
                'matching_count': count
            }
        }
    
    elif template_type == "score_threshold":
        score_type = random.choice(wellbeing_fields)
        threshold_direction = random.choice(['higher', 'lower'])
        
        if threshold_direction == 'higher':
            threshold = random.choice([5, 6, 7, 8])
            comparison = 'greater_equal'
            direction = 'higher'
        else:
            threshold = random.choice([2, 3, 4, 5])
            comparison = 'less_equal'
            direction = 'lower'
        
        count = count_respondents_with_score_threshold(case_respondents, score_type, threshold, comparison)
        
        question = template.format(score_type=score_type, threshold=threshold, direction=direction)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_type],
            'filter_conditions': [{'field': score_type, 'threshold': threshold, 'comparison': comparison}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_threshold_filter',
                'score_field': score_type,
                'threshold': threshold,
                'comparison': comparison,
                'matching_count': count
            }
        }
    
    else:  # two_conditions
        # Get available socio-economic statuses and birth years
        statuses = list(set([r['answers'].get('Socio-economic status') for r in case_respondents 
                           if r['answers'].get('Socio-economic status') is not None]))
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                         if r['answers'].get('Year of birth') is not None]))
        
        if statuses and years:
            status = random.choice(statuses)
            year = random.choice(years)
            
            conditions = [
                {'field': 'Socio-economic status', 'value': status, 'comparison': 'equal'},
                {'field': 'Year of birth', 'value': year, 'comparison': 'equal'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(status=int(status), year=int(year))
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Socio-economic status', 'Year of birth'],
                'filter_conditions': conditions,
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'two_condition_filter',
                    'conditions': conditions,
                    'matching_count': count
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Worry', 'Depression', 'Stress', 'Loneliness']
    
    templates = [
        ("three_conditions", "Count the respondents born in {year} who have a '{score_a}' greater than {threshold_a} and a '{score_b}' less than {threshold_b}."),
        ("total_score", "Count the respondents whose total score for '{score_a}' and '{score_b}' is exactly {total}."),
        ("gender_education_satisfaction", "Count the {gender} respondents whose mother has more than {education_years} years of education and whose 'Life satisfaction' is {satisfaction_threshold} or higher.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "three_conditions":
        # Get available birth years
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                         if r['answers'].get('Year of birth') is not None]))
        
        if years and len(wellbeing_fields) >= 2:
            year = random.choice(years)
            score_a, score_b = random.sample(wellbeing_fields, 2)
            threshold_a = random.choice([5, 6, 7])
            threshold_b = random.choice([3, 4, 5])
            
            conditions = [
                {'field': 'Year of birth', 'value': year, 'comparison': 'equal'},
                {'field': score_a, 'threshold': threshold_a, 'comparison': 'greater'},
                {'field': score_b, 'threshold': threshold_b, 'comparison': 'less'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(
                year=int(year), score_a=score_a, threshold_a=threshold_a,
                score_b=score_b, threshold_b=threshold_b
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', score_a, score_b],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'three_condition_filter',
                    'conditions': conditions,
                    'matching_count': count
                }
            }
    
    elif template_type == "total_score":
        if len(wellbeing_fields) >= 2:
            score_a, score_b = random.sample(wellbeing_fields, 2)
            total = random.choice([10, 12, 15, 18, 20])  # Reasonable totals for 0-10 scales
            
            score_fields = [score_a, score_b]
            count = count_respondents_with_total_score(case_respondents, score_fields, total)
            
            question = template.format(score_a=score_a, score_b=score_b, total=total)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': [score_a, score_b],
                'filter_conditions': [{'calculated_field': 'total_score', 'score_fields': score_fields, 'target_total': total}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'total_score_exact',
                    'score_fields': score_fields,
                    'target_total': total,
                    'matching_count': count
                }
            }
    
    else:  # gender_education_satisfaction
        # Get available genders
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                           if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema)
            education_years = random.choice([10, 12, 15])
            satisfaction_threshold = random.choice([6, 7, 8])
            
            conditions = [
                {'field': 'Gender', 'value': gender_code, 'comparison': 'equal'},
                {'field': 'Parental Education-Mother', 'threshold': education_years, 'comparison': 'greater'},
                {'field': 'Life satisfaction', 'threshold': satisfaction_threshold, 'comparison': 'greater_equal'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(
                gender=gender_text.lower(), education_years=education_years, 
                satisfaction_threshold=satisfaction_threshold
            )
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender', 'Parental Education-Mother', 'Life satisfaction'],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'gender_education_satisfaction_filter',
                    'gender': {'code': gender_code, 'text': gender_text},
                    'education_years': education_years,
                    'satisfaction_threshold': satisfaction_threshold,
                    'matching_count': count
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    wellbeing_fields = ['Life satisfaction', 'Happiness', 'Worry', 'Depression', 'Stress', 'Loneliness']
    
    templates = [
        ("above_gender_average", "Count the respondents whose '{score_type}' is higher than the average '{score_type}' for their gender."),
        ("above_year_average", "Count the respondents who were born in a year where the average 'Life satisfaction' for that year was greater than the overall average 'Life satisfaction'."),
        ("above_socioeconomic_depressive", "Count the respondents whose total 'Depressive Symptoms' score is higher than the average for their 'Socio-economic status' group."),
        ("below_gender_combined", "Count the respondents whose combined '{score_a}' and '{score_b}' score is lower than the average combined '{score_a}' and '{score_b}' score for their gender.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_gender_average":
        score_type = random.choice(wellbeing_fields)
        count = count_respondents_above_gender_average(case_respondents, score_type)
        
        question = template.format(score_type=score_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Gender', score_type],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_gender_average',
                'score_field': score_type,
                'matching_count': count
            }
        }
    
    elif template_type == "above_year_average":
        # Calculate overall average life satisfaction
        all_satisfaction = []
        for resp in case_respondents:
            satisfaction = resp['answers'].get('Life satisfaction')
            if satisfaction is not None:
                try:
                    all_satisfaction.append(float(satisfaction))
                except (ValueError, TypeError):
                    pass
        
        if all_satisfaction:
            overall_avg = statistics.mean(all_satisfaction)
            
            # Find years with above-average life satisfaction
            birth_years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                                  if r['answers'].get('Year of birth') is not None]))
            
            qualifying_years = []
            for year in birth_years:
                year_avg = calculate_average_for_birth_year(case_respondents, year, 'Life satisfaction')
                if year_avg > overall_avg:
                    qualifying_years.append(year)
            
            # Count respondents born in qualifying years
            count = sum(1 for r in case_respondents if r['answers'].get('Year of birth') in qualifying_years)
            
            question = template
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', 'Life satisfaction'],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_year_average_life_satisfaction',
                    'overall_average': overall_avg,
                    'qualifying_years': qualifying_years,
                    'matching_count': count
                }
            }
    
    elif template_type == "above_socioeconomic_depressive":
        # Calculate total depressive score and compare to socio-economic status group average
        count = count_respondents_above_socioeconomic_average(case_respondents, 'total_depressive_symptoms')
        
        # We need to manually calculate this since it's a computed field
        manual_count = 0
        for resp in case_respondents:
            resp_status = resp['answers'].get('Socio-economic status')
            resp_depressive = calculate_total_depressive_score(resp)
            
            if resp_status and resp_depressive > 0:
                # Calculate average for this socio-economic status
                status_respondents = [r for r in case_respondents if r['answers'].get('Socio-economic status') == resp_status]
                status_depressive_scores = [calculate_total_depressive_score(r) for r in status_respondents]
                status_depressive_scores = [s for s in status_depressive_scores if s > 0]
                
                if status_depressive_scores:
                    status_avg = statistics.mean(status_depressive_scores)
                    if resp_depressive > status_avg:
                        manual_count += 1
        
        question = template
        answer = str(manual_count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Socio-economic status', 'Depressive Symptoms'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_socioeconomic_depressive_average',
                'matching_count': manual_count
            }
        }
    
    else:  # below_gender_combined
        if len(wellbeing_fields) >= 2:
            score_a, score_b = random.sample(wellbeing_fields, 2)
            count = count_respondents_below_gender_combined_average(case_respondents, score_a, score_b)
            
            question = template.format(score_a=score_a, score_b=score_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender', score_a, score_b],
                'filter_conditions': [],
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'below_gender_combined_average',
                    'score_fields': [score_a, score_b],
                    'matching_count': count
                }
            }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health respondent count using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/respondent_count/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/mental_health_respondent_count_qa.json"
    
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