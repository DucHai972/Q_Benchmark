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

def extract_feature_values(respondents, features):
    """Extract all chosen features from respondents in this case only."""
    feature_values = {}
    
    for feature in features:
        feature_values[feature] = {}
        for resp in respondents:
            respondent_id = resp['respondent']
            raw_value = resp['answers'].get(feature)
            feature_values[feature][respondent_id] = raw_value
    
    return feature_values

def find_respondents_by_criteria(respondents, criteria):
    """Find all respondents matching the given criteria within this case."""
    matching_respondents = []
    
    for resp in respondents:
        matches = True
        for field, expected_value in criteria.items():
            actual_value = resp['answers'].get(field)
            if actual_value != expected_value:
                matches = False
                break
        
        if matches:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_country(respondents, country):
    """Find all respondents from a specific country within this case."""
    matching_respondents = []
    
    for resp in respondents:
        if resp['answers'].get('Country') == country:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_experience_threshold(respondents, field, threshold, comparison='greater'):
    """Find all respondents with experience compared to threshold within this case."""
    matching_respondents = []
    
    for resp in respondents:
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

def find_respondents_by_language(respondents, language):
    """Find all respondents who have worked with a specific language within this case."""
    matching_respondents = []
    
    for resp in respondents:
        languages = resp['answers'].get('LanguageHaveWorkedWith', '')
        if languages and language in languages.split(';'):
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_tool(respondents, tool):
    """Find all respondents who have worked with a specific tool within this case."""
    matching_respondents = []
    
    for resp in respondents:
        tools = resp['answers'].get('ToolsTechHaveWorkedWith', '')
        if tools and tool in tools.split(';'):
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

def find_respondents_by_compensation_range(respondents, min_comp, max_comp):
    """Find all respondents with compensation in given range within this case."""
    matching_respondents = []
    
    for resp in respondents:
        comp = resp['answers'].get('CompTotal')
        if comp is not None:
            try:
                numeric_comp = float(comp)
                if min_comp <= numeric_comp <= max_comp:
                    matching_respondents.append(resp['respondent'])
            except (ValueError, TypeError):
                pass
    
    return matching_respondents

def find_respondents_by_multiple_criteria(respondents, country, edlevel, language):
    """Find respondents matching multiple criteria within this case."""
    matching_respondents = []
    
    for resp in respondents:
        country_match = resp['answers'].get('Country') == country if country else True
        edlevel_match = resp['answers'].get('EdLevel') == edlevel if edlevel else True
        
        languages = resp['answers'].get('LanguageHaveWorkedWith', '')
        language_match = language in languages.split(';') if language and languages else (not language)
        
        if country_match and edlevel_match and language_match:
            matching_respondents.append(resp['respondent'])
    
    return matching_respondents

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
    """Get top N most desired languages for a specific group within this case."""
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
        ("country", "Which respondents are from '{country}'?"),
        ("experience", "Find all respondents with more than {years} years of professional coding experience."),
        ("language", "List all respondents who have worked with the '{language}' language.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country":
        # Find respondents from specific country
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        if countries:
            country = random.choice(countries)
            matching_respondents = find_respondents_by_country(case_respondents, country)
            
            question = template.format(country=country)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Country'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['Country'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_filter',
                    'criteria': {'Country': country},
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "experience":
        # Find respondents by years of professional experience
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
                matching_respondents = find_respondents_by_experience_threshold(case_respondents, 'YearsCodePro', threshold, 'greater')
                
                question = template.format(years=threshold)
                answer = ', '.join(matching_respondents) if matching_respondents else 'None'
                
                feature_values = extract_feature_values(case_respondents, ['YearsCodePro'])
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': ['YearsCodePro'],
                    'matching_respondents': matching_respondents,
                    'reasoning_complexity': 1,
                    'feature_values': feature_values,
                    'case_respondent_count': len(case_respondents),
                    'calculation_details': {
                        'method': 'experience_threshold',
                        'field': 'YearsCodePro',
                        'threshold': threshold,
                        'comparison': 'greater',
                        'matches_found': len(matching_respondents)
                    }
                }
    
    else:  # language
        # Find respondents who have worked with specific language
        all_languages = set()
        for resp in case_respondents:
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            if languages:
                all_languages.update(languages.split(';'))
        
        common_languages = ['JavaScript', 'Python', 'TypeScript', 'Java', 'C#', 'SQL', 'HTML/CSS', 'Go', 'Rust', 'C++']
        available_languages = [lang for lang in common_languages if lang in all_languages]
        
        if available_languages:
            language = random.choice(available_languages)
            matching_respondents = find_respondents_by_language(case_respondents, language)
            
            question = template.format(language=language)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['LanguageHaveWorkedWith'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Easy",
                'question': question,
                'answer': answer,
                'selected_features': ['LanguageHaveWorkedWith'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 1,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'language_filter',
                    'language': language,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_medium_question(case_id, case_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("country_education_language", "Find all respondents from '{country}' with an education level of '{edlevel}' who have worked with '{language}'."),
        ("experience_range_tool", "Which respondents have between {min_years} and {max_years} years of total coding experience and work with the '{tool}' tool?"),
        ("compensation_no_vcs", "List all respondents whose yearly compensation is over {amount} and who do not use '{vcs}' for version control.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "country_education_language":
        # Find respondents by country, education, and language
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
            
            matching_respondents = find_respondents_by_multiple_criteria(case_respondents, country, edlevel, language)
            
            question = template.format(country=country, edlevel=edlevel_text, language=language)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['Country', 'EdLevel', 'LanguageHaveWorkedWith'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['Country', 'EdLevel', 'LanguageHaveWorkedWith'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 3,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'country_education_language_filter',
                    'criteria': {
                        'Country': country,
                        'EdLevel': {'raw': edlevel, 'decoded': edlevel_text},
                        'Language': language
                    },
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "experience_range_tool":
        # Find respondents with experience in range and using specific tool
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
        
        common_tools = ['Docker', 'npm', 'Kubernetes', 'Terraform', 'Homebrew', 'Yarn', 'Ansible', 'Unity 3D', 'Unreal Engine']
        available_tools = [tool for tool in common_tools if tool in all_tools]
        
        if experiences and available_tools:
            min_years = random.choice([2, 5, 8])
            max_years = min_years + random.choice([5, 10, 15])
            tool = random.choice(available_tools)
            
            # Find respondents matching both criteria
            exp_matches = []
            for resp in case_respondents:
                exp = resp['answers'].get('YearsCode')
                if exp is not None:
                    try:
                        if min_years <= float(exp) <= max_years:
                            exp_matches.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            tool_matches = find_respondents_by_tool(case_respondents, tool)
            matching_respondents = list(set(exp_matches) & set(tool_matches))
            
            question = template.format(min_years=min_years, max_years=max_years, tool=tool)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['YearsCode', 'ToolsTechHaveWorkedWith'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['YearsCode', 'ToolsTechHaveWorkedWith'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 3,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'experience_range_tool_filter',
                    'experience_range': [min_years, max_years],
                    'tool': tool,
                    'exp_matches': len(exp_matches),
                    'tool_matches': len(tool_matches),
                    'matches_found': len(matching_respondents)
                }
            }
    
    elif template_type == "compensation_no_vcs":
        # Find respondents with high compensation not using specific VCS
        compensations = []
        for resp in case_respondents:
            comp = resp['answers'].get('CompTotal')
            if comp is not None:
                try:
                    compensations.append(float(comp))
                except (ValueError, TypeError):
                    pass
        
        vcs_options = ['Git', 'Mercurial', 'SVN']
        
        if compensations:
            threshold = random.choice([50000, 75000, 100000, 150000])
            vcs = random.choice(vcs_options)
            vcs_code = {'Git': 'A', 'Mercurial': 'B', 'SVN': 'C'}[vcs]
            
            matching_respondents = []
            for resp in case_respondents:
                comp = resp['answers'].get('CompTotal')
                resp_vcs = resp['answers'].get('VersionControlSystem')
                
                if comp is not None:
                    try:
                        if float(comp) > threshold and resp_vcs != vcs_code:
                            matching_respondents.append(resp['respondent'])
                    except (ValueError, TypeError):
                        pass
            
            question = template.format(amount=threshold, vcs=vcs)
            answer = ', '.join(matching_respondents) if matching_respondents else 'None'
            
            feature_values = extract_feature_values(case_respondents, ['CompTotal', 'VersionControlSystem'])
            
            return {
                'case_id': case_id,
                'difficulty_mode': "Medium",
                'question': question,
                'answer': answer,
                'selected_features': ['CompTotal', 'VersionControlSystem'],
                'matching_respondents': matching_respondents,
                'reasoning_complexity': 3,
                'feature_values': feature_values,
                'case_respondent_count': len(case_respondents),
                'calculation_details': {
                    'method': 'compensation_no_vcs_filter',
                    'compensation_threshold': threshold,
                    'excluded_vcs': vcs,
                    'matches_found': len(matching_respondents)
                }
            }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, case_respondents, features, questions_schema)

def generate_hard_question(case_id, case_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    templates = [
        ("above_country_average", "Find all respondents whose total compensation is higher than the average compensation for their country."),
        ("above_edlevel_experience", "Which respondents have more professional coding experience than the average for their education level?"),
        ("top_languages_orgsize", "List all respondents who have worked with a language that is also one of the top 3 most desired languages among all respondents in their same organization size.")
    ]
    
    template_type, template = random.choice(templates)
    
    if template_type == "above_country_average":
        # Find respondents above their country average compensation
        matching_respondents = []
        
        # Calculate averages by country within this case
        countries = list(set([r['answers'].get('Country') for r in case_respondents 
                            if r['answers'].get('Country') is not None]))
        
        country_averages = {}
        for country in countries:
            country_average = calculate_average_for_group(case_respondents, 'CompTotal', 'Country', country)
            if country_average > 0:
                country_averages[country] = country_average
        
        # Find respondents above their country average
        for resp in case_respondents:
            country = resp['answers'].get('Country')
            comp = resp['answers'].get('CompTotal')
            
            if country and comp is not None and country in country_averages:
                try:
                    if float(comp) > country_averages[country]:
                        matching_respondents.append(resp['respondent'])
                except (ValueError, TypeError):
                    pass
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        feature_values = extract_feature_values(case_respondents, ['Country', 'CompTotal'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['Country', 'CompTotal'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_country_average_compensation',
                'country_averages': country_averages,
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "above_edlevel_experience":
        # Find respondents above their education level average experience
        matching_respondents = []
        
        # Calculate averages by education level within this case
        edlevels = list(set([r['answers'].get('EdLevel') for r in case_respondents 
                           if r['answers'].get('EdLevel') is not None]))
        
        edlevel_averages = {}
        for edlevel in edlevels:
            edlevel_average = calculate_average_for_group(case_respondents, 'YearsCodePro', 'EdLevel', edlevel)
            if edlevel_average > 0:
                edlevel_averages[edlevel] = edlevel_average
        
        # Find respondents above their education level average
        for resp in case_respondents:
            edlevel = resp['answers'].get('EdLevel')
            exp = resp['answers'].get('YearsCodePro')
            
            if edlevel and exp is not None and edlevel in edlevel_averages:
                try:
                    if float(exp) > edlevel_averages[edlevel]:
                        matching_respondents.append(resp['respondent'])
                except (ValueError, TypeError):
                    pass
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        feature_values = extract_feature_values(case_respondents, ['EdLevel', 'YearsCodePro'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['EdLevel', 'YearsCodePro'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'above_edlevel_experience_average',
                'edlevel_averages': {k: v for k, v in edlevel_averages.items()},
                'matches_found': len(matching_respondents)
            }
        }
    
    elif template_type == "top_languages_orgsize":
        # Find respondents who work with top desired languages for their org size
        matching_respondents = []
        
        # Get organization sizes
        orgsizes = list(set([r['answers'].get('OrgSize') for r in case_respondents 
                           if r['answers'].get('OrgSize') is not None]))
        
        # Calculate top languages for each org size within this case
        orgsize_top_languages = {}
        for orgsize in orgsizes:
            top_langs = get_top_languages_for_group(case_respondents, 'OrgSize', orgsize)
            if top_langs:
                orgsize_top_languages[orgsize] = top_langs
        
        # Find respondents who work with top languages for their org size
        for resp in case_respondents:
            orgsize = resp['answers'].get('OrgSize')
            languages = resp['answers'].get('LanguageHaveWorkedWith', '')
            
            if orgsize and languages and orgsize in orgsize_top_languages:
                resp_languages = set(languages.split(';'))
                top_languages = set(orgsize_top_languages[orgsize])
                
                if resp_languages & top_languages:  # If intersection is not empty
                    matching_respondents.append(resp['respondent'])
        
        question = template
        answer = ', '.join(matching_respondents) if matching_respondents else 'None'
        
        feature_values = extract_feature_values(case_respondents, ['OrgSize', 'LanguageHaveWorkedWith', 'LanguageWantToWorkWith'])
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Really Hard",
            'question': question,
            'answer': answer,
            'selected_features': ['OrgSize', 'LanguageHaveWorkedWith', 'LanguageWantToWorkWith'],
            'matching_respondents': matching_respondents,
            'reasoning_complexity': 5,
            'feature_values': feature_values,
            'case_respondent_count': len(case_respondents),
            'calculation_details': {
                'method': 'top_languages_by_orgsize',
                'orgsize_top_languages': orgsize_top_languages,
                'matches_found': len(matching_respondents)
            }
        }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, case_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for stack-overflow answer reverse lookup using case-specific data."""
    
    # Paths
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/stack-overflow-2022/answer_reverse_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/stack-overflow-2022/stack-overflow-2022_answer_reverse_lookup_qa.json"
    
    # Load features from actual data structure
    sample_case = os.path.join(data_dir, "case_1.json")
    with open(sample_case, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Get actual feature names from the questions schema
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