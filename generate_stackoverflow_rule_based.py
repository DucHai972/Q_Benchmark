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

def calculate_yearly_compensation(respondent):
    """Calculate yearly compensation based on CompTotal and CompFreq."""
    comp_total = respondent['answers'].get('CompTotal')
    comp_freq = respondent['answers'].get('CompFreq')
    
    if comp_total is None or comp_freq is None:
        return None
    
    try:
        comp_value = float(comp_total)
        
        if comp_freq == 'A':  # Weekly
            return comp_value * 52
        elif comp_freq == 'B':  # Monthly
            return comp_value * 12
        elif comp_freq == 'C':  # Yearly
            return comp_value
        else:
            return None
    except (ValueError, TypeError):
        return None

def find_respondents_with_numerical_rule(respondents, field, threshold, comparison):
    """Find respondents meeting numerical rule."""
    matching_respondents = []
    
    for resp in respondents:
        value = resp['answers'].get(field)
        if value is not None:
            try:
                num_value = float(value)
                
                if comparison == 'greater' and num_value > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and num_value < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and num_value == threshold:
                    matching_respondents.append(resp)
                elif comparison == 'between' and isinstance(threshold, tuple):
                    min_val, max_val = threshold
                    if min_val <= num_value <= max_val:
                        matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_country_and_numerical_rule(respondents, country, field, threshold, comparison):
    """Find respondents from specific country meeting numerical rule."""
    matching_respondents = []
    
    for resp in respondents:
        resp_country = resp['answers'].get('Country')
        value = resp['answers'].get(field)
        
        if resp_country == country and value is not None:
            try:
                num_value = float(value)
                
                if comparison == 'greater' and num_value > threshold:
                    matching_respondents.append(resp)
                elif comparison == 'less' and num_value < threshold:
                    matching_respondents.append(resp)
                elif comparison == 'equal' and num_value == threshold:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_with_yearly_compensation_rule(respondents, threshold, comparison):
    """Find respondents with yearly compensation meeting rule."""
    matching_respondents = []
    
    for resp in respondents:
        yearly_comp = calculate_yearly_compensation(resp)
        if yearly_comp is not None:
            if comparison == 'greater' and yearly_comp > threshold:
                matching_respondents.append(resp)
            elif comparison == 'less' and yearly_comp < threshold:
                matching_respondents.append(resp)
            elif comparison == 'equal' and yearly_comp == threshold:
                matching_respondents.append(resp)
    
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
            
            if field == 'yearly_compensation':
                resp_value = calculate_yearly_compensation(resp)
            else:
                resp_value = resp['answers'].get(field)
            
            if comparison == 'equal':
                if resp_value != value:
                    meets_all_conditions = False
                    break
            elif comparison in ['greater', 'less']:
                if resp_value is None:
                    meets_all_conditions = False
                    break
                try:
                    resp_num = float(resp_value)
                    thresh_num = float(threshold)
                    
                    if comparison == 'greater' and resp_num <= thresh_num:
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

def find_respondents_with_coding_years_comparison(respondents):
    """Find respondents where professional years < half of total years."""
    matching_respondents = []
    
    for resp in respondents:
        years_code = resp['answers'].get('YearsCode')
        years_code_pro = resp['answers'].get('YearsCodePro')
        
        if years_code is not None and years_code_pro is not None:
            try:
                total_years = float(years_code)
                pro_years = float(years_code_pro)
                
                if pro_years < (total_years / 2):
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def calculate_average_for_group(respondents, group_field, group_value, value_field):
    """Calculate average value for specific group."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        if value_field == 'yearly_compensation':
            val = calculate_yearly_compensation(resp)
        else:
            val = resp['answers'].get(value_field)
        
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def find_respondents_above_group_average(respondents, group_field, value_field):
    """Find respondents with value above their group's average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        
        if value_field == 'yearly_compensation':
            resp_value = calculate_yearly_compensation(resp)
        else:
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

def find_respondents_with_compensation_multiple_of_education_average(respondents, multiplier):
    """Find respondents with yearly compensation > multiplier * education group average."""
    matching_respondents = []
    
    for resp in respondents:
        resp_education = resp['answers'].get('EdLevel')
        resp_comp = calculate_yearly_compensation(resp)
        
        if resp_education and resp_comp is not None:
            try:
                resp_comp_num = float(resp_comp)
                edu_avg = calculate_average_for_group(respondents, 'EdLevel', resp_education, 'yearly_compensation')
                
                if resp_comp_num > multiplier * edu_avg:
                    matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_within_percentage_of_highest(respondents, group_field, value_field, percentage):
    """Find respondents within percentage of highest value in their group."""
    matching_respondents = []
    
    for resp in respondents:
        resp_group = resp['answers'].get(group_field)
        
        if value_field == 'yearly_compensation':
            resp_value = calculate_yearly_compensation(resp)
        else:
            resp_value = resp['answers'].get(value_field)
        
        if resp_group and resp_value is not None:
            try:
                resp_num = float(resp_value)
                
                # Find highest value in the group
                group_respondents = [r for r in respondents if r['answers'].get(group_field) == resp_group]
                group_values = []
                
                for group_resp in group_respondents:
                    if value_field == 'yearly_compensation':
                        group_val = calculate_yearly_compensation(group_resp)
                    else:
                        group_val = group_resp['answers'].get(value_field)
                    
                    if group_val is not None:
                        try:
                            group_values.append(float(group_val))
                        except (ValueError, TypeError):
                            pass
                
                if group_values:
                    highest_value = max(group_values)
                    threshold = highest_value * (1 - percentage / 100)
                    
                    if resp_num >= threshold:
                        matching_respondents.append(resp)
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    # Numerical fields
    numerical_fields = ['YearsCode', 'YearsCodePro', 'CompTotal']
    
    templates = [
        ("numerical_greater", "Which respondents have a '{field}' greater than {threshold}?"),
        ("numerical_between", "Find all respondents whose '{field}' is between {min_val} and {max_val}."),
        ("country_numerical", "List all respondents from '{country}' whose '{field}' is less than {threshold}.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "numerical_greater":
        field = random.choice(numerical_fields)
        
        # Get sample values to set reasonable threshold
        values = []
        for resp in case_respondents:
            val = resp['answers'].get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        
        if values:
            if field in ['YearsCode', 'YearsCodePro']:
                threshold = random.choice([5, 10, 15])
            else:  # CompTotal
                threshold = int(statistics.median(values))
            
            matching_respondents = find_respondents_with_numerical_rule(case_respondents, field, threshold, 'greater')
            
            question = template.format(field=field, threshold=threshold)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': [field],
                'filter_conditions': [{'field': field, 'threshold': threshold, 'comparison': 'greater'}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'numerical_rule',
                    'field': field,
                    'threshold': threshold,
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "numerical_between":
        field = random.choice(numerical_fields)
        
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
            if field in ['YearsCode', 'YearsCodePro']:
                min_val = random.choice([2, 5])
                max_val = min_val + random.choice([5, 10])
            else:  # CompTotal
                min_val = int(min(values) + (max(values) - min(values)) * 0.2)
                max_val = int(min(values) + (max(values) - min(values)) * 0.8)
            
            matching_respondents = find_respondents_with_numerical_rule(case_respondents, field, (min_val, max_val), 'between')
            
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
                    'method': 'numerical_range_rule',
                    'field': field,
                    'range': [min_val, max_val],
                    'matching_count': len(matching_respondents)
                }
            }
    
    else:  # country_numerical
        # Get available countries
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                             if r['answers'].get('Country') is not None]))
        
        if countries:
            country = random.choice(countries)
            field = random.choice(numerical_fields)
            
            # Get sample values to set threshold
            values = []
            for resp in case_respondents:
                val = resp['answers'].get(field)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass
            
            if values:
                if field in ['YearsCode', 'YearsCodePro']:
                    threshold = random.choice([8, 12, 15])
                else:  # CompTotal
                    threshold = int(statistics.median(values))
                
                matching_respondents = find_respondents_with_country_and_numerical_rule(
                    case_respondents, country, field, threshold, 'less'
                )
                
                question = template.format(country=country, field=field, threshold=threshold)
                answer = [resp['respondent'] for resp in matching_respondents]
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Country', field],
                    'filter_conditions': [
                        {'field': 'Country', 'value': country},
                        {'field': field, 'threshold': threshold, 'comparison': 'less'}
                    ],
                    'reasoning_complexity': 2,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'country_numerical_rule',
                        'country': country,
                        'field': field,
                        'threshold': threshold,
                        'comparison': 'less',
                        'matching_count': len(matching_respondents)
                    }
                }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("yearly_compensation", "Find all respondents whose calculated yearly compensation is greater than {amount}."),
        ("country_multiple_conditions", "Which respondents from '{country}' have more than {years} '{years_field}' and a yearly compensation less than {amount}?"),
        ("coding_years_comparison", "List all respondents for whom their professional coding years are less than half their total coding years.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "yearly_compensation":
        # Calculate reasonable threshold based on case data
        yearly_comps = []
        for resp in case_respondents:
            yearly_comp = calculate_yearly_compensation(resp)
            if yearly_comp is not None:
                yearly_comps.append(yearly_comp)
        
        if yearly_comps:
            amount = int(statistics.median(yearly_comps))
            
            matching_respondents = find_respondents_with_yearly_compensation_rule(case_respondents, amount, 'greater')
            
            question = template.format(amount=amount)
            answer = [resp['respondent'] for resp in matching_respondents]
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['CompTotal', 'CompFreq'],
                'filter_conditions': [{'calculated_field': 'yearly_compensation', 'threshold': amount, 'comparison': 'greater'}],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'yearly_compensation_rule',
                    'threshold_amount': amount,
                    'comparison': 'greater',
                    'matching_count': len(matching_respondents)
                }
            }
    
    elif template_type == "country_multiple_conditions":
        # Get available countries
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                             if r['answers'].get('Country') is not None]))
        
        if countries:
            country = random.choice(countries)
            years_field = random.choice(['YearsCode', 'YearsCodePro'])
            years = random.choice([5, 8, 10])
            
            # Get reasonable compensation threshold
            yearly_comps = []
            for resp in case_respondents:
                yearly_comp = calculate_yearly_compensation(resp)
                if yearly_comp is not None:
                    yearly_comps.append(yearly_comp)
            
            if yearly_comps:
                amount = int(statistics.median(yearly_comps))
                
                conditions = [
                    {'field': 'Country', 'value': country, 'comparison': 'equal'},
                    {'field': years_field, 'threshold': years, 'comparison': 'greater'},
                    {'field': 'yearly_compensation', 'threshold': amount, 'comparison': 'less'}
                ]
                
                matching_respondents = find_respondents_with_multiple_conditions(case_respondents, conditions)
                
                question = template.format(country=country, years=years, years_field=years_field, amount=amount)
                answer = [resp['respondent'] for resp in matching_respondents]
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Medium",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['Country', years_field, 'CompTotal', 'CompFreq'],
                    'filter_conditions': conditions,
                    'reasoning_complexity': 3,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'country_multiple_conditions',
                        'conditions': conditions,
                        'matching_count': len(matching_respondents)
                    }
                }
    
    else:  # coding_years_comparison
        matching_respondents = find_respondents_with_coding_years_comparison(case_respondents)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Medium",
            'question': question,
            'answer': answer,
            'selected_features': ['YearsCode', 'YearsCodePro'],
            'filter_conditions': [{'calculated_field': 'coding_years_comparison', 'rule': 'professional < half of total'}],
            'reasoning_complexity': 3,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'coding_years_comparison',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_group_average", "Find all respondents whose '{field}' is greater than the average '{field}' for their {group_field}."),
        ("compensation_multiple_education", "Which respondents have a calculated yearly compensation that is more than double the average for their EdLevel?"),
        ("within_percentage_highest", "List all respondents whose '{field}' is within {percentage}% of the highest '{field}' in their {group_field}."),
        ("compensation_above_education_average", "Which respondents have a yearly compensation that is higher than the average yearly compensation for all respondents with the same education level?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_group_average":
        field = random.choice(['YearsCode', 'YearsCodePro', 'CompTotal'])
        group_field = random.choice(['Country', 'EdLevel'])
        
        matching_respondents = find_respondents_above_group_average(case_respondents, group_field, field)
        
        group_text = group_field.lower()
        
        question = template.format(field=field, group_field=group_text)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [group_field, field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_group_average',
                'group_field': group_field,
                'value_field': field,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "compensation_multiple_education":
        matching_respondents = find_respondents_with_compensation_multiple_of_education_average(case_respondents, 2.0)
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['EdLevel', 'CompTotal', 'CompFreq'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'compensation_multiple_education_average',
                'multiplier': 2.0,
                'matching_count': len(matching_respondents)
            }
        }
    
    elif template_type == "within_percentage_highest":
        field = random.choice(['YearsCode', 'CompTotal'])
        group_field = random.choice(['Country', 'EdLevel'])
        percentage = random.choice([10, 20, 25])
        
        matching_respondents = find_respondents_within_percentage_of_highest(
            case_respondents, group_field, field, percentage
        )
        
        group_text = group_field.lower()
        
        question = template.format(field=field, percentage=percentage, group_field=group_text)
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': [group_field, field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'within_percentage_highest',
                'group_field': group_field,
                'value_field': field,
                'percentage': percentage,
                'matching_count': len(matching_respondents)
            }
        }
    
    else:  # compensation_above_education_average
        matching_respondents = find_respondents_above_group_average(case_respondents, 'EdLevel', 'yearly_compensation')
        
        question = template
        answer = [resp['respondent'] for resp in matching_respondents]
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['EdLevel', 'CompTotal', 'CompFreq'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'compensation_above_education_average',
                'matching_count': len(matching_respondents)
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for stack-overflow rule-based querying using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/rule_based_querying/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stackoverflow_rule_based_qa.json"
    
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