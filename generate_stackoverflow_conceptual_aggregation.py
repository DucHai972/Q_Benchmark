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

def count_respondents_by_country(respondents, country):
    """Count respondents from specific country within this case."""
    count = 0
    
    for resp in respondents:
        if resp['answers'].get('Country') == country:
            count += 1
    
    return count

def count_respondents_by_experience_threshold(respondents, field, threshold, comparison='greater'):
    """Count respondents with experience compared to threshold within this case."""
    count = 0
    
    for resp in respondents:
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

def count_respondents_by_language(respondents, language):
    """Count respondents who have worked with specific language within this case."""
    count = 0
    
    for resp in respondents:
        languages = resp['answers'].get('LanguageHaveWorkedWith', '')
        if languages and language in languages.split(';'):
            count += 1
    
    return count

def count_respondents_by_tool(respondents, tool):
    """Count respondents who have worked with specific tool within this case."""
    count = 0
    
    for resp in respondents:
        tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
        if tools and tool in tools.split(';'):
            count += 1
    
    return count

def count_respondents_by_multiple_tools(respondents, tool_list):
    """Count respondents who have worked with all tools in the list within this case."""
    count = 0
    
    for resp in respondents:
        tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
        if tools:
            resp_tools = set(tools.split(';'))
            if all(tool in resp_tools for tool in tool_list):
                count += 1
    
    return count

def count_respondents_by_experience_range_and_tool(respondents, min_years, max_years, tool):
    """Count respondents with experience in range and using specific tool within this case."""
    count = 0
    
    for resp in respondents:
        experience = resp['answers'].get('YearsCode')
        tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
        
        if experience is not None and tools:
            try:
                exp_years = float(experience)
                if (min_years <= exp_years <= max_years and 
                    tool in tools.split(';')):
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def count_respondents_by_compensation_and_vcs(respondents, min_compensation, excluded_vcs):
    """Count respondents with high compensation not using specific VCS within this case."""
    count = 0
    
    for resp in respondents:
        compensation = resp['answers'].get('CompTotal')
        vcs = resp['answers'].get('VersionControlSystem')
        
        if compensation is not None:
            try:
                if float(compensation) > min_compensation and vcs != excluded_vcs:
                    count += 1
            except (ValueError, TypeError):
                pass
    
    return count

def calculate_average_for_group(respondents, target_field, group_field, group_value):
    """Calculate average of target_field for respondents in specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(target_field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def get_top_languages_for_group(respondents, group_field, group_value, top_n=3):
    """Get top N most desired languages for specific group within this case."""
    group_respondents = [r for r in respondents if r['answers'].get(group_field) == group_value]
    
    language_counts = {}
    for resp in group_respondents:
        languages = resp['answers'].get('LanguageWantToWorkWith', '')
        if languages:
            for lang in languages.split(';'):
                language_counts[lang] = language_counts.get(lang, 0) + 1
    
    sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    return [lang for lang, count in sorted_languages[:top_n]]

def generate_easy_question(case_id, case_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    templates = [
        ("country", "How many respondents are from '{country}'?"),
        ("experience", "Count the respondents with more than {years} years of professional coding experience."),
        ("language", "How many respondents have worked with the '{language}' language?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country":
        # Count respondents from specific country
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        if countries:
            country = random.choice(countries)
            count = count_respondents_by_country(case_respondents, country)
            
            question = template.format(country=country)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Country'],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_count',
                    'criteria': {'Country': country},
                    'count': count
                }
            }
    
    elif template_type == "experience":
        # Count respondents by years of professional experience
        experiences = [r['answers'].get('YearsCodePro') for r in case_respondents 
                      if r['answers'].get('YearsCodePro') is not None]
        
        if experiences:
            # Choose a reasonable threshold
            numeric_experiences = []
            for exp in experiences:
                try:
                    numeric_experiences.append(float(exp))
                except (ValueError, TypeError):
                    pass
            
            if numeric_experiences:
                threshold = random.choice([3, 5, 10, 15])
                count = count_respondents_by_experience_threshold(case_respondents, 'YearsCodePro', threshold, 'greater')
                
                question = template.format(years=threshold)
                answer = str(count)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['YearsCodePro'],
                    'count': count,
                    'reasoning_complexity': 1,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'experience_threshold_count',
                        'field': 'YearsCodePro',
                        'threshold': threshold,
                        'comparison': 'greater',
                        'count': count
                    }
                }
    
    else:  # language
        # Count respondents who have worked with specific language
        all_languages = set()
        for resp in case_respondents:
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            if languages:
                all_languages.update(languages.split(';'))
        
        common_languages = ['JavaScript', 'Python', 'TypeScript', 'Java', 'C#', 'SQL', 'HTML/CSS', 'Go', 'Rust', 'C++']
        available_languages = [lang for lang in common_languages if lang in all_languages]
        
        if available_languages:
            language = random.choice(available_languages)
            count = count_respondents_by_language(case_respondents, language)
            
            question = template.format(language=language)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['LanguageHaveWorkedWith'],
                'count': count,
                'reasoning_complexity': 1,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'language_count',
                    'language': language,
                    'count': count
                }
            }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("country_education_language", "How many respondents from '{country}' with an education level of '{edlevel}' have worked with '{language}'?"),
        ("experience_range_tool", "Count the respondents with between {min_years} and {max_years} years of total coding experience who work with the '{tool}' tool."),
        ("employment_multiple_tools", "How many respondents who are '{employment_status}' have worked with both '{tool_a}' and '{tool_b}'?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country_education_language":
        # Count by country, education, and language
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        edlevels = list(set([r['answers'].get('EdLevel') for r in case_respondents 
                           if r['answers'].get('EdLevel') is not None]))
        
        all_languages = set()
        for resp in case_respondents:
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            if languages:
                all_languages.update(languages.split(';'))
        
        if countries and edlevels and all_languages:
            country = random.choice(countries)
            edlevel = random.choice(edlevels)
            language = random.choice(list(all_languages))
            
            edlevel_text = decode_mcq_answer('EdLevel', edlevel, questions_schema)
            
            # Count respondents matching all criteria
            count = 0
            for resp in case_respondents:
                resp_country = resp['answers'].get('Country')
                resp_edlevel = resp['answers'].get('EdLevel')
                resp_languages = resp['answers'].get('LanguageHaveWorkedWith', '')
                
                if (resp_country == country and 
                    resp_edlevel == edlevel and 
                    resp_languages and language in resp_languages.split(';')):
                    count += 1
            
            question = template.format(country=country, edlevel=edlevel_text, language=language)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Country', 'EdLevel', 'LanguageHaveWorkedWith'],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_education_language_count',
                    'criteria': {
                        'Country': country,
                        'EdLevel': {'raw': edlevel, 'decoded': edlevel_text},
                        'Language': language
                    },
                    'count': count
                }
            }
    
    elif template_type == "experience_range_tool":
        # Count by experience range and tool usage
        experiences = []
        for resp in case_respondents:
            exp = resp['answers'].get('YearsCode')
            if exp is not None:
                try:
                    experiences.append(float(exp))
                except (ValueError, TypeError):
                    pass
        
        all_tools = set()
        for resp in case_respondents:
            tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
            if tools:
                all_tools.update(tools.split(';'))
        
        common_tools = ['Docker', 'npm', 'Kubernetes', 'Terraform', 'Homebrew', 'Yarn', 'Ansible', 'Unity 3D']
        available_tools = [tool for tool in common_tools if tool in all_tools]
        
        if experiences and available_tools:
            min_years = random.choice([2, 5, 8])
            max_years = min_years + random.choice([5, 10, 15])
            tool = random.choice(available_tools)
            
            count = count_respondents_by_experience_range_and_tool(case_respondents, min_years, max_years, tool)
            
            question = template.format(min_years=min_years, max_years=max_years, tool=tool)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['YearsCode', 'ToolsTechHaveWorkedWith'],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'experience_range_tool_count',
                    'experience_range': [min_years, max_years],
                    'tool': tool,
                    'count': count
                }
            }
    
    elif template_type == "employment_multiple_tools":
        # Count by employment status and multiple tools
        employment_statuses = list(set([r['answers'].get('Employment') for r in case_respondents 
                                      if r['answers'].get('Employment') is not None]))
        
        all_tools = set()
        for resp in case_respondents:
            tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
            if tools:
                all_tools.update(tools.split(';'))
        
        if employment_statuses and len(all_tools) >= 2:
            employment_code = random.choice(employment_statuses)
            employment_text = decode_mcq_answer('Employment', employment_code, questions_schema)
            tool_a, tool_b = random.sample(list(all_tools), 2)
            
            # Count respondents with specific employment and both tools
            count = 0
            for resp in case_respondents:
                resp_employment = resp['answers'].get('Employment')
                resp_tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
                
                if (resp_employment == employment_code and resp_tools):
                    tools_set = set(resp_tools.split(';'))
                    if tool_a in tools_set and tool_b in tools_set:
                        count += 1
            
            question = template.format(employment_status=employment_text, tool_a=tool_a, tool_b=tool_b)
            answer = str(count)
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Employment', 'ToolsTechHaveWorkedWith'],
                'count': count,
                'reasoning_complexity': 3,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'employment_multiple_tools_count',
                    'employment': {'raw': employment_code, 'decoded': employment_text},
                    'tools': [tool_a, tool_b],
                    'count': count
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_country_compensation", "How many respondents have a total compensation (yearly) that is higher than the average compensation for their country?"),
        ("above_edlevel_experience", "Count the respondents who have more professional coding experience than the average for their education level."),
        ("top_languages_orgsize", "How many respondents have worked with a language that is also one of the top 3 most desired languages among all respondents in their same organization size?")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_country_compensation":
        # Count respondents above their country's average compensation
        # Calculate averages by country within this case
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        country_averages = {}
        for country in countries:
            country_average = calculate_average_for_group(case_respondents, 'CompTotal', 'Country', country)
            if country_average > 0:
                country_averages[country] = country_average
        
        # Count respondents above their country average
        count = 0
        for resp in case_respondents:
            country = resp['answers'].get('Country')
            compensation = resp['answers'].get('CompTotal')
            
            if country and compensation is not None and country in country_averages:
                try:
                    if float(compensation) > country_averages[country]:
                        count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Country', 'CompTotal'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_country_compensation_average_count',
                'country_averages': country_averages,
                'count': count
            }
        }
    
    elif template_type == "above_edlevel_experience":
        # Count respondents above their education level average experience
        # Calculate averages by education level within this case
        edlevels = list(set([r['answers'].get('EdLevel') for r in case_respondents 
                           if r['answers'].get('EdLevel') is not None]))
        
        edlevel_averages = {}
        for edlevel in edlevels:
            edlevel_average = calculate_average_for_group(case_respondents, 'YearsCodePro', 'EdLevel', edlevel)
            if edlevel_average > 0:
                edlevel_averages[edlevel] = edlevel_average
        
        # Count respondents above their education level average
        count = 0
        for resp in case_respondents:
            edlevel = resp['answers'].get('EdLevel')
            experience = resp['answers'].get('YearsCodePro')
            
            if edlevel and experience is not None and edlevel in edlevel_averages:
                try:
                    if float(experience) > edlevel_averages[edlevel]:
                        count += 1
                except (ValueError, TypeError):
                    pass
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['EdLevel', 'YearsCodePro'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_edlevel_experience_average_count',
                'edlevel_averages': {decode_mcq_answer('EdLevel', k, questions_schema): v 
                                    for k, v in edlevel_averages.items()},
                'count': count
            }
        }
    
    elif template_type == "top_languages_orgsize":
        # Count respondents who work with top desired languages for their org size
        # Get organization sizes
        orgsizes = list(set([r['answers'].get('OrgSize') for r in case_respondents 
                           if r['answers'].get('OrgSize') is not None]))
        
        # Calculate top languages for each org size within this case
        orgsize_top_languages = {}
        for orgsize in orgsizes:
            top_langs = get_top_languages_for_group(case_respondents, 'OrgSize', orgsize)
            if top_langs:
                orgsize_top_languages[orgsize] = top_langs
        
        # Count respondents who work with top languages for their org size
        count = 0
        for resp in case_respondents:
            orgsize = resp['answers'].get('OrgSize')
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            
            if orgsize and languages and orgsize in orgsize_top_languages:
                resp_languages = set(languages.split(';'))
                top_languages = set(orgsize_top_languages[orgsize])
                
                if resp_languages & top_languages:  # If intersection is not empty
                    count += 1
        
        question = template
        answer = str(count)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['OrgSize', 'LanguageHaveWorkedWith', 'LanguageWantToWorkWith'],
            'count': count,
            'reasoning_complexity': 5,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'top_languages_by_orgsize_count',
                'orgsize_top_languages': orgsize_top_languages,
                'count': count
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for stack-overflow conceptual aggregation using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/conceptual_aggregation/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stack-overflow-2022_conceptual_aggregation_qa.json"
    
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