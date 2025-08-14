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

def count_respondents_by_criteria(respondents, criteria):
    """Count respondents matching the given criteria within this case."""
    count = 0
    
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
            count += 1
    
    return count

def count_respondents_by_gender(respondents, gender_code, questions_schema):
    """Count respondents by gender within this case."""
    count = 0
    
    for resp in respondents:
        if resp['answers'].get('Gender') == gender_code:
            count += 1
    
    return count

def count_respondents_by_score_threshold(respondents, field, threshold, comparison='greater_equal'):
    """Count respondents with score compared to threshold within this case."""
    count = 0
    
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
                    (comparison == 'equal' and numeric_value == threshold) or
                    (comparison == 'greater_equal' and numeric_value >= threshold) or
                    (comparison == 'less_equal' and numeric_value <= threshold)):
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_by_dual_criteria(respondents, field_a, threshold_a, comparison_a, field_b, threshold_b, comparison_b):
    """Count respondents meeting two numeric criteria within this case."""
    count = 0
    
    for resp in respondents:
        # Handle nested features for field_a
        if '.' in field_a:
            main_feature, sub_feature = field_a.split('.', 1)
            value_a = resp['answers'].get(main_feature, {})
            if isinstance(value_a, dict):
                value_a = value_a.get(sub_feature)
            else:
                value_a = None
        else:
            value_a = resp['answers'].get(field_a)
        
        # Handle nested features for field_b
        if '.' in field_b:
            main_feature, sub_feature = field_b.split('.', 1)
            value_b = resp['answers'].get(main_feature, {})
            if isinstance(value_b, dict):
                value_b = value_b.get(sub_feature)
            else:
                value_b = None
        else:
            value_b = resp['answers'].get(field_b)
        
        if value_a is not None and value_b is not None:
            try:
                num_a = float(value_a)
                num_b = float(value_b)
                
                criteria_a_met = False
                criteria_b_met = False
                
                if comparison_a == 'greater' and num_a > threshold_a:
                    criteria_a_met = True
                elif comparison_a == 'less' and num_a < threshold_b:
                    criteria_a_met = True
                elif comparison_a == 'greater_equal' and num_a >= threshold_a:
                    criteria_a_met = True
                elif comparison_a == 'less_equal' and num_a <= threshold_a:
                    criteria_a_met = True
                
                if comparison_b == 'greater' and num_b > threshold_b:
                    criteria_b_met = True
                elif comparison_b == 'less' and num_b < threshold_b:
                    criteria_b_met = True
                elif comparison_b == 'greater_equal' and num_b >= threshold_b:
                    criteria_b_met = True
                elif comparison_b == 'less_equal' and num_b <= threshold_b:
                    criteria_b_met = True
                
                if criteria_a_met and criteria_b_met:
                    count += 1
                    
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_by_total_score(respondents, fields, target_total):
    """Count respondents with exact combined score within this case."""
    count = 0
    
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
            count += 1
    
    return count

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
    """Calculate total score for a symptom category."""
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
        ("gender_count", "How many respondents are {gender}?"),
        ("score_threshold", "Count the respondents with a {score_field} of {threshold} or higher."),
        ("ses_year_combo", "How many respondents with a 'Socio-economic status' of {ses} were born in {year}?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "gender_count":
        # Count by gender
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema).lower()
            
            count = count_respondents_by_gender(case_respondents, gender_code, questions_schema)
            
            question = template.format(gender=gender_text)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender'],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'gender_count',
                    'criteria': {'Gender': {'raw': gender_code, 'decoded': gender_text}},
                    'count': count
                }
            }
    
    elif template_type == "score_threshold":
        # Count by score threshold
        score_field = random.choice(wellbeing_features)
        threshold = random.choice([5, 6, 7, 8])  # Mid to high thresholds
        
        count = count_respondents_by_score_threshold(case_respondents, score_field, threshold, 'greater_equal')
        
        question = template.format(score_field=score_field, threshold=threshold)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [score_field],
            'count': count,
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'score_threshold_count',
                'score_field': score_field,
                'threshold': threshold,
                'comparison': 'greater_equal',
                'count': count
            }
        }
    
    else:  # ses_year_combo
        # Count by socio-economic status and birth year
        ses_values = list(set([r['answers'].get('Socio-economic status') for r in case_respondents 
                             if r['answers'].get('Socio-economic status') is not None]))
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                        if r['answers'].get('Year of birth') is not None]))
        
        if ses_values and years:
            ses = random.choice(ses_values)
            year = random.choice(years)
            
            criteria = {'Socio-economic status': ses, 'Year of birth': year}
            count = count_respondents_by_criteria(case_respondents, criteria)
            
            question = template.format(ses=ses, year=int(year))
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Socio-economic status', 'Year of birth'],
                'count': count,
                'reasoning_complexity': 2,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'ses_year_count',
                    'criteria': criteria,
                    'count': count
                }
            }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                         'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("year_dual_scores", "How many respondents born in {year} have a {score_a} greater than {threshold_a} and a {score_b} less than {threshold_b}?"),
        ("total_score_exact", "Count the respondents whose total score for '{score_a}' and '{score_b}' is exactly {total}."),
        ("gender_education_satisfaction", "How many {gender} respondents have a mother with more than {education_years} years of education and a 'Life satisfaction' score of {satisfaction_threshold} or higher?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "year_dual_scores":
        # Count by birth year + dual score criteria
        years = list(set([r['answers'].get('Year of birth') for r in case_respondents 
                        if r['answers'].get('Year of birth') is not None]))
        
        if years and len(wellbeing_features) >= 2:
            year = random.choice(years)
            score_a, score_b = random.sample(wellbeing_features, 2)
            threshold_a = random.choice([4, 5, 6])
            threshold_b = random.choice([4, 5, 6])
            
            # Count respondents meeting all criteria
            count = 0
            for resp in case_respondents:
                birth_year = resp['answers'].get('Year of birth')
                val_a = resp['answers'].get(score_a)
                val_b = resp['answers'].get(score_b)
                
                if birth_year == year and val_a is not None and val_b is not None:
                    try:
                        if float(val_a) > threshold_a and float(val_b) < threshold_b:
                            count += 1
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(year=int(year), score_a=score_a, threshold_a=threshold_a,
                                     score_b=score_b, threshold_b=threshold_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', score_a, score_b],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'year_dual_scores_count',
                    'criteria': {
                        'Year of birth': year,
                        f'{score_a}_greater': threshold_a,
                        f'{score_b}_less': threshold_b
                    },
                    'count': count
                }
            }
    
    elif template_type == "total_score_exact":
        # Count by exact combined score
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
                count = count_respondents_by_total_score(case_respondents, [score_a, score_b], target_total)
                
                question = template.format(score_a=score_a, score_b=score_b, total=target_total)
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
                        'method': 'exact_total_score_count',
                        'score_fields': [score_a, score_b],
                        'target_total': target_total,
                        'count': count
                    }
                }
    
    elif template_type == "gender_education_satisfaction":
        # Count by gender + mother's education + life satisfaction
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        if genders:
            gender_code = random.choice(genders)
            gender_text = decode_mcq_answer('Gender', gender_code, questions_schema).lower()
            education_years = random.choice([15, 16, 17, 18])
            satisfaction_threshold = random.choice([6, 7, 8])
            
            # Count respondents meeting all criteria
            count = 0
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
                            count += 1
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(gender=gender_text, education_years=education_years,
                                     satisfaction_threshold=satisfaction_threshold)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Gender', 'Parental Education.Mother', 'Life satisfaction'],
                'count': count,
                'reasoning_complexity': 4,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'gender_education_satisfaction_count',
                    'criteria': {
                        'Gender': {'raw': gender_code, 'decoded': gender_text},
                        'Mother_education_greater': education_years,
                        'Life_satisfaction_min': satisfaction_threshold
                    },
                    'count': count
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    wellbeing_features = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment',
                         'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
    
    templates = [
        ("above_gender_average", "How many respondents have a {score_field} that is higher than the average {score_field} for their gender?"),
        ("above_year_average", "Count the respondents who were born in a year where the average 'Life satisfaction' for that year was greater than the overall average 'Life satisfaction'."),
        ("above_ses_depressive_avg", "How many respondents have a total 'Depressive Symptoms' score that is higher than the average for their 'Socio-economic status' group?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_gender_average":
        # Count respondents above their gender average
        score_field = random.choice(wellbeing_features)
        
        # Calculate averages by gender within this case
        genders = list(set([r['answers'].get('Gender') for r in case_respondents 
                          if r['answers'].get('Gender') is not None]))
        
        gender_averages = {}
        for gender in genders:
            gender_average = calculate_average_for_group(case_respondents, score_field, 'Gender', gender)
            gender_averages[gender] = gender_average
        
        # Count respondents above their gender average
        count = 0
        for resp in case_respondents:
            gender = resp['answers'].get('Gender')
            score = resp['answers'].get(score_field)
            
            if gender and score is not None and gender in gender_averages:
                try:
                    if float(score) > gender_averages[gender]:
                        count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template.format(score_field=score_field)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [score_field, 'Gender'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_gender_average_count',
                'score_field': score_field,
                'gender_averages': {decode_mcq_answer('Gender', k, questions_schema): v 
                                   for k, v in gender_averages.items()},
                'count': count
            }
        }
    
    elif template_type == "above_year_average":
        # Count respondents born in high life satisfaction years
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
            
            # Count respondents born in qualifying years
            count = 0
            for resp in case_respondents:
                birth_year = resp['answers'].get('Year of birth')
                if birth_year in qualifying_years:
                    count += 1
            
            question = template
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Really Hard",
                'question': question,
                'answer': answer,
                'selected_features': ['Year of birth', 'Life satisfaction'],
                'count': count,
                'reasoning_complexity': 5,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'above_year_average_life_satisfaction_count',
                    'overall_average': overall_average,
                    'qualifying_years': qualifying_years,
                    'count': count
                }
            }
    
    elif template_type == "above_ses_depressive_avg":
        # Count respondents with depressive symptoms above their SES group average
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
        
        # Count respondents above their SES group average
        count = 0
        for resp in case_respondents:
            ses = resp['answers'].get('Socio-economic status')
            if ses and ses in ses_averages:
                total_score = calculate_total_symptom_score(resp, 'Depressive Symptoms Frequency')
                if total_score > ses_averages[ses]:
                    count += 1
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Socio-economic status', 'Depressive Symptoms Frequency'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_ses_depressive_symptoms_average_count',
                'ses_averages': ses_averages,
                'count': count
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for self-reported-mental-health conceptual aggregation using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/conceptual_aggregation/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/self-reported-mental-health_conceptual_aggregation_qa.json"
    
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