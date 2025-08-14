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

def count_respondents_from_country(respondents, country):
    """Count respondents from specific country."""
    count = 0
    for resp in respondents:
        if resp['answers'].get('Country') == country:
            count += 1
    return count

def count_respondents_with_experience_threshold(respondents, field, threshold, comparison='greater'):
    """Count respondents with experience meeting threshold."""
    count = 0
    for resp in respondents:
        experience = resp['answers'].get(field)
        if experience is not None:
            try:
                exp_num = float(experience)
                if comparison == 'greater' and exp_num > threshold:
                    count += 1
                elif comparison == 'greater_equal' and exp_num >= threshold:
                    count += 1
                elif comparison == 'less' and exp_num < threshold:
                    count += 1
                elif comparison == 'between' and isinstance(threshold, tuple):
                    min_val, max_val = threshold
                    if min_val <= exp_num <= max_val:
                        count += 1
            except (ValueError, TypeError):
                pass
    return count

def count_respondents_with_language(respondents, language):
    """Count respondents who have worked with specific language."""
    count = 0
    for resp in respondents:
        languages = resp['answers'].get('LanguageHaveWorkedWith', '')
        if languages and isinstance(languages, str):
            language_list = [lang.strip() for lang in languages.split(';')]
            if language in language_list:
                count += 1
    return count

def count_respondents_with_tool(respondents, tool):
    """Count respondents who have used specific tool."""
    count = 0
    for resp in respondents:
        tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
        if tools and isinstance(tools, str):
            tool_list = [t.strip() for t in tools.split(';')]
            if tool in tool_list:
                count += 1
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
            languages = condition.get('languages', [])
            tools = condition.get('tools', [])
            
            resp_value = resp['answers'].get(field)
            
            if comparison == 'equal':
                if resp_value != value:
                    meets_all_conditions = False
                    break
            elif comparison in ['greater', 'greater_equal', 'less']:
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
            elif comparison == 'contains_language':
                resp_languages = resp_value or ''
                if isinstance(resp_languages, str):
                    lang_list = [lang.strip() for lang in resp_languages.split(';')]
                    for required_lang in languages:
                        if required_lang not in lang_list:
                            meets_all_conditions = False
                            break
                else:
                    meets_all_conditions = False
                    break
            elif comparison == 'contains_tool':
                resp_tools = resp_value or ''
                if isinstance(resp_tools, str):
                    tool_list = [tool.strip() for tool in resp_tools.split(';')]
                    for required_tool in tools:
                        if required_tool not in tool_list:
                            meets_all_conditions = False
                            break
                else:
                    meets_all_conditions = False
                    break
        
        if meets_all_conditions:
            count += 1
    
    return count

def calculate_average_compensation_for_country(respondents, country):
    """Calculate average compensation for specific country."""
    country_respondents = [r for r in respondents if r['answers'].get('Country') == country]
    
    values = []
    for resp in country_respondents:
        comp = resp['answers'].get('CompTotal')
        if comp is not None:
            try:
                values.append(float(comp))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def calculate_average_experience_for_education(respondents, education_level, field):
    """Calculate average experience for specific education level."""
    edu_respondents = [r for r in respondents if r['answers'].get('EdLevel') == education_level]
    
    values = []
    for resp in edu_respondents:
        exp = resp['answers'].get(field)
        if exp is not None:
            try:
                values.append(float(exp))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def get_top_languages(respondents, top_n=3):
    """Get top N most desired languages among all respondents."""
    language_counts = {}
    
    for resp in respondents:
        desired_languages = resp['answers'].get('LanguageWantToWorkWith', '')
        if desired_languages and isinstance(desired_languages, str):
            lang_list = [lang.strip() for lang in desired_languages.split(';')]
            for lang in lang_list:
                if lang:  # Skip empty strings
                    language_counts[lang] = language_counts.get(lang, 0) + 1
    
    # Sort by count and get top N
    sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    return [lang for lang, count in sorted_languages[:top_n]]

def count_respondents_above_country_compensation_average(respondents):
    """Count respondents whose compensation is higher than their country's average."""
    count = 0
    
    for resp in respondents:
        resp_country = resp['answers'].get('Country')
        resp_comp = resp['answers'].get('CompTotal')
        
        if resp_country and resp_comp is not None:
            try:
                resp_comp_num = float(resp_comp)
                country_avg = calculate_average_compensation_for_country(respondents, resp_country)
                
                if resp_comp_num > country_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_above_education_experience_average(respondents, experience_field):
    """Count respondents with experience above their education level's average."""
    count = 0
    
    for resp in respondents:
        resp_education = resp['answers'].get('EdLevel')
        resp_experience = resp['answers'].get(experience_field)
        
        if resp_education and resp_experience is not None:
            try:
                resp_exp_num = float(resp_experience)
                edu_avg = calculate_average_experience_for_education(respondents, resp_education, experience_field)
                
                if resp_exp_num > edu_avg:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_with_top_desired_languages(respondents):
    """Count respondents who have worked with a top 3 most desired language."""
    top_languages = get_top_languages(respondents, 3)
    
    count = 0
    for resp in respondents:
        worked_languages = resp['answers'].get('LanguageHaveWorkedWith', '')
        if worked_languages and isinstance(worked_languages, str):
            worked_list = [lang.strip() for lang in worked_languages.split(';')]
            
            # Check if any worked language is in top desired
            for lang in worked_list:
                if lang in top_languages:
                    count += 1
                    break
    
    return count

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    templates = [
        ("country", "Count the respondents from '{country}'."),
        ("experience", "Count the respondents with more than {years} years of {experience_type}."),
        ("language", "Count the respondents who have worked with the '{language}' language."),
        ("tool", "Count the respondents who have used '{tool}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country":
        # Get available countries
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        if countries:
            country = random.choice(countries)
            count = count_respondents_from_country(case_respondents, country)
            
            question = template.format(country=country)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Country'],
                'filter_conditions': [{'field': 'Country', 'value': country}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_filter',
                    'country': country,
                    'matching_count': count
                }
            }
    
    elif template_type == "experience":
        experience_fields = {'total coding experience': 'YearsCode', 'professional coding experience': 'YearsCodePro'}
        experience_type = random.choice(list(experience_fields.keys()))
        field = experience_fields[experience_type]
        years = random.choice([3, 5, 7, 10, 15])
        
        count = count_respondents_with_experience_threshold(case_respondents, field, years, 'greater')
        
        question = template.format(years=years, experience_type=experience_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': [field],
            'filter_conditions': [{'field': field, 'threshold': years, 'comparison': 'greater'}],
            'reasoning_complexity': 1,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'experience_threshold',
                'experience_field': field,
                'threshold': years,
                'comparison': 'greater',
                'matching_count': count
            }
        }
    
    elif template_type == "language":
        # Get available languages from the data
        all_languages = set()
        for resp in case_respondents:
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            if languages and isinstance(languages, str):
                lang_list = [lang.strip() for lang in languages.split(';')]
                all_languages.update(lang_list)
        
        available_languages = [lang for lang in all_languages if lang]  # Remove empty strings
        
        if available_languages:
            language = random.choice(available_languages)
            count = count_respondents_with_language(case_respondents, language)
            
            question = template.format(language=language)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['LanguageHaveWorkedWith'],
                'filter_conditions': [{'field': 'LanguageHaveWorkedWith', 'language': language}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'language_filter',
                    'language': language,
                    'matching_count': count
                }
            }
    
    else:  # tool
        # Get available tools from the data
        all_tools = set()
        for resp in case_respondents:
            tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
            if tools and isinstance(tools, str):
                tool_list = [tool.strip() for tool in tools.split(';')]
                all_tools.update(tool_list)
        
        available_tools = [tool for tool in all_tools if tool]  # Remove empty strings
        
        if available_tools:
            tool = random.choice(available_tools)
            count = count_respondents_with_tool(case_respondents, tool)
            
            question = template.format(tool=tool)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['ToolsTechHaveWorkedWith'],
                'filter_conditions': [{'field': 'ToolsTechHaveWorkedWith', 'tool': tool}],
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'tool_filter',
                    'tool': tool,
                    'matching_count': count
                }
            }
    
    return None

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("country_education_language", "Count the respondents from '{country}' with an education level of '{education}' who have worked with '{language}'."),
        ("experience_range_tool", "Count the respondents with between {min_years} and {max_years} years of total coding experience who work with the '{tool}' tool."),
        ("employment_compensation", "Count the respondents who are '{employment_status}' and whose yearly compensation is over {amount}."),
        ("employment_tools_languages", "Count the respondents who are '{employment_status}', use '{tool}', and have worked with '{language}'.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country_education_language":
        # Get available values
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        educations = list(set([r['answers'].get('EdLevel') for r in case_respondents 
                             if r['answers'].get('EdLevel') is not None]))
        
        # Get available languages
        all_languages = set()
        for resp in case_respondents:
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            if languages and isinstance(languages, str):
                lang_list = [lang.strip() for lang in languages.split(';')]
                all_languages.update(lang_list)
        available_languages = [lang for lang in all_languages if lang]
        
        if countries and educations and available_languages:
            country = random.choice(countries)
            education = random.choice(educations)
            language = random.choice(available_languages)
            
            education_text = decode_mcq_answer('EdLevel', education, questions_schema)
            
            conditions = [
                {'field': 'Country', 'value': country, 'comparison': 'equal'},
                {'field': 'EdLevel', 'value': education, 'comparison': 'equal'},
                {'field': 'LanguageHaveWorkedWith', 'languages': [language], 'comparison': 'contains_language'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(country=country, education=education_text, language=language)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Country', 'EdLevel', 'LanguageHaveWorkedWith'],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_education_language_filter',
                    'country': country,
                    'education': {'code': education, 'text': education_text},
                    'language': language,
                    'matching_count': count
                }
            }
    
    elif template_type == "experience_range_tool":
        min_years = random.choice([3, 5, 7])
        max_years = min_years + random.choice([5, 10, 15])
        
        # Get available tools
        all_tools = set()
        for resp in case_respondents:
            tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
            if tools and isinstance(tools, str):
                tool_list = [tool.strip() for tool in tools.split(';')]
                all_tools.update(tool_list)
        available_tools = [tool for tool in all_tools if tool]
        
        if available_tools:
            tool = random.choice(available_tools)
            
            # Count manually since we need range check
            count = 0
            for resp in case_respondents:
                years_code = resp['answers'].get('YearsCode')
                resp_tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
                
                if years_code is not None and resp_tools:
                    try:
                        years_num = float(years_code)
                        tool_list = [t.strip() for t in resp_tools.split(';')]
                        
                        if min_years <= years_num <= max_years and tool in tool_list:
                            count += 1
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(min_years=min_years, max_years=max_years, tool=tool)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['YearsCode', 'ToolsTechHaveWorkedWith'],
                'filter_conditions': [
                    {'field': 'YearsCode', 'min_years': min_years, 'max_years': max_years, 'comparison': 'range'},
                    {'field': 'ToolsTechHaveWorkedWith', 'tool': tool, 'comparison': 'contains_tool'}
                ],
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'experience_range_tool_filter',
                    'experience_range': [min_years, max_years],
                    'tool': tool,
                    'matching_count': count
                }
            }
    
    elif template_type == "employment_compensation":
        # Get available employment statuses
        employments = list(set([r['answers'].get('Employment') for r in case_respondents 
                              if r['answers'].get('Employment') is not None]))
        
        if employments:
            employment = random.choice(employments)
            employment_text = decode_mcq_answer('Employment', employment, questions_schema)
            amount = random.choice([50000, 75000, 100000, 150000])
            
            conditions = [
                {'field': 'Employment', 'value': employment, 'comparison': 'equal'},
                {'field': 'CompTotal', 'threshold': amount, 'comparison': 'greater'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(employment_status=employment_text, amount=amount)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Employment', 'CompTotal'],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'employment_compensation_filter',
                    'employment': {'code': employment, 'text': employment_text},
                    'compensation_threshold': amount,
                    'matching_count': count
                }
            }
    
    else:  # employment_tools_languages
        # Get available values
        employments = list(set([r['answers'].get('Employment') for r in case_respondents 
                              if r['answers'].get('Employment') is not None]))
        
        # Get available tools and languages
        all_tools = set()
        all_languages = set()
        for resp in case_respondents:
            tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            
            if tools and isinstance(tools, str):
                tool_list = [tool.strip() for tool in tools.split(';')]
                all_tools.update(tool_list)
            
            if languages and isinstance(languages, str):
                lang_list = [lang.strip() for lang in languages.split(';')]
                all_languages.update(lang_list)
        
        available_tools = [tool for tool in all_tools if tool]
        available_languages = [lang for lang in all_languages if lang]
        
        if employments and available_tools and available_languages:
            employment = random.choice(employments)
            tool = random.choice(available_tools)
            language = random.choice(available_languages)
            
            employment_text = decode_mcq_answer('Employment', employment, questions_schema)
            
            conditions = [
                {'field': 'Employment', 'value': employment, 'comparison': 'equal'},
                {'field': 'ToolsTechHaveWorkedWith', 'tools': [tool], 'comparison': 'contains_tool'},
                {'field': 'LanguageHaveWorkedWith', 'languages': [language], 'comparison': 'contains_language'}
            ]
            
            count = count_respondents_with_multiple_conditions(case_respondents, conditions)
            
            question = template.format(employment_status=employment_text, tool=tool, language=language)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Employment', 'ToolsTechHaveWorkedWith', 'LanguageHaveWorkedWith'],
                'filter_conditions': conditions,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'employment_tools_languages_filter',
                    'employment': {'code': employment, 'text': employment_text},
                    'tool': tool,
                    'language': language,
                    'matching_count': count
                }
            }
    
    return None

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("compensation_above_country_avg", "Count the respondents whose total compensation (yearly) is higher than the average compensation for their country."),
        ("experience_above_education_avg", "Count the respondents who have more {experience_type} than the average for their education level."),
        ("top_desired_languages", "Count the respondents who have worked with a language that is also one of the top 3 most desired languages among all respondents.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "compensation_above_country_avg":
        count = count_respondents_above_country_compensation_average(case_respondents)
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Country', 'CompTotal'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'compensation_above_country_average',
                'matching_count': count
            }
        }
    
    elif template_type == "experience_above_education_avg":
        experience_types = {
            'professional coding experience': 'YearsCodePro',
            'total coding experience': 'YearsCode'
        }
        experience_type = random.choice(list(experience_types.keys()))
        field = experience_types[experience_type]
        
        count = count_respondents_above_education_experience_average(case_respondents, field)
        
        question = template.format(experience_type=experience_type)
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['EdLevel', field],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'experience_above_education_average',
                'experience_field': field,
                'experience_type': experience_type,
                'matching_count': count
            }
        }
    
    else:  # top_desired_languages
        count = count_respondents_with_top_desired_languages(case_respondents)
        top_languages = get_top_languages(case_respondents, 3)
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['LanguageHaveWorkedWith', 'LanguageWantToWorkWith'],
            'filter_conditions': [],
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'top_desired_languages',
                'top_3_desired_languages': top_languages,
                'matching_count': count
            }
        }
    
    return None

def main():
    """Generate 50 question-answer pairs for stack-overflow-2022 respondent count using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/respondent_count/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stackoverflow_respondent_count_qa.json"
    
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