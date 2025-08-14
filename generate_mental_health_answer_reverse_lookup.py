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
    
    # Parse options like "1. Male 2. Female"
    parts = mcq_part.strip().split()
    current_key = None
    current_value = []
    
    for part in parts:
        if part.endswith('.'):
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[:-1]  # Remove the dot
            current_value = []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(str(int(coded_answer)), str(coded_answer))

def extract_feature_values(respondents, features):
    """Extract all chosen features from respondents in this case only."""
    feature_values = {}
    
    for feature in features:
        feature_values[feature] = {}
        for resp in respondents:
            respondent_id = resp['respondent']
            # Handle nested features
            if '.' in feature:
                main_feature, sub_feature = feature.split('.', 1)
                value = resp['answers'].get(main_feature, {})
                if isinstance(value, dict):
                    raw_value = value.get(sub_feature)
                else:
                    raw_value = None
            else:
                raw_value = resp['answers'].get(feature)
            feature_values[feature][respondent_id] = raw_value
    
    return feature_values

def find_respondents_by_criteria(respondents, criteria):
    """Find all respondents matching the given criteria within this case."""
    matching_respondents = []
    
    for resp in respondents:
        matches = True
        for field, expected_value in criteria.items():
            # Handle nested features
            if '.' in field:
                main_feature, sub_feature = field.split('.', 1)
                actual_value = resp['answers'].get(main_feature, {})
                if isinstance(actual_value, dict):
                    actual_value = actual_value.get(sub_feature)
                else:
                    actual_value = None
            else:
                actual_value = resp['answers'].get(field)
            
            if actual_value != expected_value:
                matches = False
                break
        
        if matches:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_range(respondents, field, min_val, max_val):
    """Find all respondents with field value in given range within this case."""
    matching_respondents = []
    
    for resp in respondents:
        # Handle nested features
        if '.' in field:
            main_feature, sub_feature = field.split('.', 1)
            value = resp['answers'].get(main_feature, {})
            if isinstance(value, dict):
                value = value.get(sub_feature)
            else:
                value = None
        else:
            value = resp['answers'].get(field)
        
        if value is not None:
            try:
                numeric_value = float(value)
                if min_val <= numeric_value <= max_val:
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_by_comparison(respondents, field, threshold, comparison):
    """Find all respondents with field value compared to threshold within this case."""
    matching_respondents = []
    
    for resp in respondents:
        # Handle nested features
        if '.' in field:
            main_feature, sub_feature = field.split('.', 1)
            value = resp['answers'].get(main_feature, {})
            if isinstance(value, dict):
                value = value.get(sub_feature)
            else:
                value = None
        else:
            value = resp['answers'].get(field)
        
        if value is not None:
            try:
                numeric_value = float(value)
                if ((comparison == 'greater' and numeric_value > threshold) or
                    (comparison == 'less' and numeric_value < threshold) or
                    (comparison == 'equal' and numeric_value == threshold)):
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_by_total_score(respondents, fields, target_total):
    """Find all respondents with exact combined score within this case."""
    matching_respondents = []
    
    for resp in respondents:
        total_score = 0
        valid_scores = 0
        
        for field in fields:
            # Handle nested features
            if '.' in field:
                main_feature, sub_feature = field.split('.', 1)
                value = resp['answers'].get(main_feature, {})
                if isinstance(value, dict):
                    value = value.get(sub_feature)
                else:
                    value = None
            else:
                value = resp['answers'].get(field)
            
            if value is not None:
                try:
                    total_score += float(value)
                    valid_scores += 1
                except (ValueError, TypeError):
                    pass
        
        # Only consider if all scores are available
        if valid_scores == len(fields) and total_score == target_total:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def calculate_average_for_group(respondents, target_field, group_field, group_value):
    """Calculate average of target_field for respondents in specific group within this case."""
    group_respondents = []
    for resp in respondents:
        # Handle nested group field
        if '.' in group_field:
            main_feature, sub_feature = group_field.split('.', 1)
            resp_value = resp['answers'].get(main_feature, {})
            if isinstance(resp_value, dict):
                resp_value = resp_value.get(sub_feature)
            else:
                resp_value = None
        else:
            resp_value = resp['answers'].get(group_field)
        
        if resp_value == group_value:
            group_respondents.append(resp)
    
    values = []
    for resp in group_respondents:
        # Handle nested target field
        if '.' in target_field:
            main_feature, sub_feature = target_field.split('.', 1)
            value = resp['answers'].get(main_feature, {})
            if isinstance(value, dict):
                value = value.get(sub_feature)
            else:
                value = None
        else:
            value = resp['answers'].get(target_field)
        
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_total_symptom_score(respondent, symptom_category):
    """Calculate total score for a symptom category (e.g., Depressive Symptoms Frequency)."""
    category_data = respondent['answers'].get(symptom_category, {})
    if not isinstance(category_data, dict):
        return 0
    
    total = 0
    count = 0
    for sub_field, value in category_data.items():
        if value is not None:
            try:
                total += float(value)
                count += 1
            except (ValueError, TypeError):
                pass
    
    return total if count > 0 else 0

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Basic demographic features
    basic_features = ['Year of birth', 'Gender', 'Socio-economic status', 'Ethnic identity']
    
    # Well-being features (0-10 scale)
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                         'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("single_demographic", "Which respondents are {demographic_value}?"),
        ("single_score", "Find all respondents with a {score_field} of {score_value}."),
        ("demographic_year", "List all respondents with a '{demographic_field}' of {demographic_value} who were born in {year}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "single_demographic":
        # Find respondents by single demographic criterion
        field = random.choice(basic_features)
        
        # Get possible values for this field within this case
        possible_values = list(set([r['answers'].get(field) for r in case_respondents 
                                  if r['answers'].get(field) is not None]))
        
        if possible_values:
            raw_value = random.choice(possible_values)
            
            if field == 'Gender':
                decoded_value = decode_mcq_answer(field, raw_value, questions_schema).lower()
            else:
                decoded_value = str(raw_value)
            
            matching_respondents = find_respondents_by_criteria(case_respondents, {field: raw_value})
            
            question = template.format(demographic_value=decoded_value)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [field])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'single_demographic_filter',
                    'criteria': {field: {'raw': raw_value, 'decoded': decoded_value}},
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "single_score":
        # Find respondents by single score criterion
        field = random.choice(wellbeing_features)
        
        # Get possible scores for this field within this case
        possible_scores = list(set([r['answers'].get(field) for r in case_respondents 
                                  if r['answers'].get(field) is not None]))
        
        if possible_scores:
            score_value = random.choice(possible_scores)
            matching_respondents = find_respondents_by_criteria(case_respondents, {field: score_value})
            
            question = template.format(score_field=field, score_value=int(score_value))
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [field])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'single_score_filter',
                    'criteria': {field: score_value},
                    'matches_found': len(matching_respondents)
                }
            }
    
    else:  # demographic_year
        # Find respondents by demographic + birth year
        demographic_field = random.choice([f for f in basic_features if f != 'Year of birth'])
        
        # Get possible values within this case
        demo_values = list(set([r['answers'].get(demographic_field) for r in case_respondents 
                              if r['answers'].get(demographic_field) is not None]))
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                        if r['answers'].get('Year of birth') is not None]))
        
        if demo_values and years:
            raw_demo_value = random.choice(demo_values)
            year = random.choice(years)
            
            if demographic_field == 'Gender':
                decoded_demo_value = decode_mcq_answer(demographic_field, raw_demo_value, questions_schema)
            else:
                decoded_demo_value = str(raw_demo_value)
            
            criteria = {demographic_field: raw_demo_value, 'Year of birth': year}
            matching_respondents = find_respondents_by_criteria(case_respondents, criteria)
            
            question = template.format(demographic_field=demographic_field, 
                                     demographic_value=decoded_demo_value, year=int(year))
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, [demographic_field, 'Year of birth'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [demographic_field, 'Year of birth'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 2,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'demographic_year_filter',
                    'criteria': {
                        demographic_field: {'raw': raw_demo_value, 'decoded': decoded_demo_value},
                        'Year of birth': year
                    },
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                         'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("year_dual_scores", "Find all respondents born in {year} with a {score_a} greater than {threshold_a} and a {score_b} less than {threshold_b}."),
        ("exact_total_score", "Which respondents have a total score for '{score_a}' and '{score_b}' of exactly {total}?"),
        ("gender_education_satisfaction", "List all {gender} respondents whose mother has more than {education_years} years of education and whose 'Life satisfaction' is {satisfaction_threshold} or higher.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "year_dual_scores":
        # Find respondents by birth year + dual score criteria
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                        if r['answers'].get('Year of birth') is not None]))
        
        if years and len(wellbeing_features) >= 2:
            year = random.choice(years)
            score_a, score_b = random.sample(wellbeing_features, 2)
            
            # Get reasonable thresholds based on data within this case
            scores_a = [r['answers'].get(score_a) for r in case_respondents 
                       if r['answers'].get(score_a) is not None]
            scores_b = [r['answers'].get(score_b) for r in case_respondents 
                       if r['answers'].get(score_b) is not None]
            
            if scores_a and scores_b:
                threshold_a = random.choice([4, 5, 6])  # Mid-range threshold
                threshold_b = random.choice([4, 5, 6])
                
                # Find matching respondents
                matching_respondents = []
                for resp in case_respondents:
                    birth_year = resp['answers'].get('Year of birth')
                    val_a = resp['answers'].get(score_a)
                    val_b = resp['answers'].get(score_b)
                    
                    if (birth_year == year and val_a is not None and val_b is not None):
                        try:
                            if float(val_a) > threshold_a and float(val_b) < threshold_b:
                                matching_respondents.append(resp['respondent'])
                        except (ValueError, TypeError):
                            pass
                
                question = template.format(year=int(year), score_a=score_a, threshold_a=threshold_a,
                                         score_b=score_b, threshold_b=threshold_b)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['Year of birth', score_a, score_b])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Year of birth', score_a, score_b],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 3,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'year_dual_score_filter',
                        'criteria': {
                            'Year of birth': year,
                            f'{score_a}_greater': threshold_a,
                            f'{score_b}_less': threshold_b
                        },
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "exact_total_score":
        # Find respondents with exact combined score
        if len(wellbeing_features) >= 2:
            score_a, score_b = random.sample(wellbeing_features, 2)
            
            # Calculate possible totals from this case
            possible_totals = []
            for resp in case_respondents:
                val_a = resp['answers'].get(score_a)
                val_b = resp['answers'].get(score_b)
                if val_a is not None and val_b is not None:
                    try:
                        total = float(val_a) + float(val_b)
                        possible_totals.append(int(total))
                    except (ValueError, TypeError):
                        pass
            
            if possible_totals:
                target_total = random.choice(possible_totals)
                matching_respondents = find_respondents_by_total_score(case_respondents, [score_a, score_b], target_total)
                
                question = template.format(score_a=score_a, score_b=score_b, total=target_total)
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
                        'method': 'exact_total_score',
                        'score_fields': [score_a, score_b],
                        'target_total': target_total,
                        'matches_found': len(matching_respondents)
                    }
                }
    
    elif template_type == "gender_education_satisfaction":
        # Complex filter: gender + mother's education + life satisfaction
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema).lower()
            education_years = random.choice([15, 16, 17, 18])
            satisfaction_threshold = random.choice([6, 7, 8])
            
            # Find matching respondents
            matching_respondents = []
            for resp in case_respondents:
                resp_gender = resp['answers'].get('Gender')
                parental_ed = resp['answers'].get('Parental Education', {})
                mother_ed = parental_ed.get('Mother') if isinstance(parental_ed, dict) else None
                life_sat = resp['answers'].get('Life satisfaction')
                
                if (resp_gender == gender_code and 
                    mother_ed is not None and life_sat is not None):
                    try:
                        if (float(mother_ed) > education_years and 
                            float(life_sat) >= satisfaction_threshold):
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(gender=gender_text, education_years=education_years,
                                     satisfaction_threshold=satisfaction_threshold)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Gender', 'Parental Education.Mother', 'Life satisfaction'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender', 'Parental Education.Mother', 'Life satisfaction'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 4,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'gender_education_satisfaction_filter',
                    'criteria': {
                        'Gender': {'raw': gender_code, 'decoded': gender_text},
                        'Mother_education_greater': education_years,
                        'Life_satisfaction_min': satisfaction_threshold
                    },
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                         'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("above_gender_average", "Find all respondents whose {score_field} is higher than the average {score_field} for their gender."),
        ("above_year_average", "Which respondents were born in a year where the average 'Life satisfaction' for that year was greater than the overall average 'Life satisfaction'?"),
        ("above_ses_average", "List all respondents whose total 'Depressive Symptoms' score is higher than the average for their 'Socio-economic status' group.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_gender_average":
        # Find respondents above their gender average
        score_field = random.choice(wellbeing_features)
        matching_respondents = []
        
        # Calculate averages by gender within this case
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        gender_averages = {}
        for gender in genders:
            gender_average = calculate_average_for_group(case_respondents, score_field, 'Gender', gender)
            gender_averages[gender] = gender_average
        
        # Find respondents above their gender average
        for resp in case_respondents:
            gender = resp['answers'].get('Gender')
            score = resp['answers'].get(score_field)
            
            if gender and score is not None and gender in gender_averages:
                try:
                    if float(score) > gender_averages[gender]:
                        matching_respondents.append(resp['respondent'])
                except (ValueError, TypeError):
                    pass
        
        question = template.format(score_field=score_field)
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        feature_values = extract_feature_values(case_respondents, [score_field, 'Gender'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [score_field, 'Gender'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_gender_average',
                'score_field': score_field,
                'gender_averages': gender_averages,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "above_year_average":
        # Find respondents born in high life satisfaction years
        # Calculate overall average life satisfaction within this case
        all_life_sat = [r['answers'].get('Life satisfaction') for r in case_respondents 
                       if r['answers'].get('Life satisfaction') is not None]
        
        if all_life_sat:
            overall_average = statistics.mean([float(x) for x in all_life_sat])
            
            # Calculate averages by birth year within this case
            years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                            if r['answers'].get('Year of birth') is not None]))
            
            qualifying_years = []
            for year in years:
                year_average = calculate_average_for_group(case_respondents, 'Life satisfaction', 'Year of birth', year)
                if year_average > overall_average:
                    qualifying_years.append(year)
            
            # Find respondents born in qualifying years
            matching_respondents = []
            for resp in case_respondents:
                birth_year = resp['answers'].get('Year of birth')
                if birth_year in qualifying_years:
                    matching_respondents.append(resp['respondent'])
            
            question = template
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Year of birth', 'Life satisfaction'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', 'Life satisfaction'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 5,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_year_average_life_satisfaction',
                    'overall_average': overall_average,
                    'qualifying_years': qualifying_years,
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "above_ses_average":
        # Find respondents with depressive symptoms above their SES group average
        matching_respondents = []
        
        # Calculate averages by socio-economic status within this case
        ses_values = list(set([r['answers'].get('Socio-economic status') for r in case_respondents 
                             if r['answers'].get('Socio-economic status') is not None]))
        
        ses_averages = {}
        for ses in ses_values:
            # Calculate average total depressive symptoms for this SES group
            group_totals = []
            for resp in case_respondents:
                if resp['answers'].get('Socio-economic status') == ses:
                    total_score = calculate_total_symptom_score(resp, 'Depressive Symptoms Frequency')
                    if total_score > 0:
                        group_totals.append(total_score)
            
            ses_averages[ses] = statistics.mean(group_totals) if group_totals else 0
        
        # Find respondents above their SES group average
        for resp in case_respondents:
            ses = resp['answers'].get('Socio-economic status')
            if ses and ses in ses_averages:
                total_score = calculate_total_symptom_score(resp, 'Depressive Symptoms Frequency')
                if total_score > ses_averages[ses]:
                    matching_respondents.append(resp['respondent'])
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        # Use a representative depressive symptom field for feature values
        feature_values = extract_feature_values(case_respondents, ['Socio-economic status', 'Depressive Symptoms Frequency.Depressed Mood'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Socio-economic status', 'Depressive Symptoms Frequency.Depressed Mood'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_ses_depressive_symptoms_average',
                'ses_averages': ses_averages,
                'matches_found': len(matching_respondents)
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health answer reverse lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_reverse_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/self-reported-mental-health_answer_reverse_lookup_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names including nested ones
    features = []
    for key in sample_data['questions'].keys():
        if key != 'respondent':
            if isinstance(sample_data['questions'][key], dict) and 'sub_questions' in sample_data['questions'][key]:
                # Handle nested features
                for sub_key in sample_data['questions'][key]['sub_questions'].keys():
                    features.append(f"{key}.{sub_key}")
            else:
                features.append(key)
    
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