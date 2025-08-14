#!/usr/bin/env python3
import json
import csv
import random
import os
import statistics
from pathlib import Path

def load_all_case_data(data_dir, num_cases=50):
    """Load ALL case data for comprehensive validation."""
    all_data = {}
    questions_schema = None
    all_respondents = []
    
    for i in range(1, num_cases + 1):
        case_file = os.path.join(data_dir, f"case_{i}.json")
        if os.path.exists(case_file):
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
                all_data[f"case_{i}"] = case_data
                
                # Store schema from first case
                if questions_schema is None:
                    questions_schema = case_data['questions']
                
                # Collect all respondents
                for resp in case_data['responses']:
                    resp['source_case'] = f"case_{i}"
                    all_respondents.append(resp)
    
    return all_data, questions_schema, all_respondents

def decode_mcq_answer(feature, coded_answer, questions_schema):
    """Decode MCQ answer from letter code to human-readable text."""
    question_text = questions_schema[feature]
    
    if '[MCQ:' not in question_text:
        return coded_answer
    
    # Extract MCQ options
    mcq_part = question_text.split('[MCQ:')[1].split(']')[0]
    options = {}
    
    # Parse options like "A. Female B. Male" 
    parts = mcq_part.strip().split()
    current_key = None
    current_value = []
    
    for part in parts:
        if len(part) == 2 and part[1] == '.':
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[0]
            current_value = []
        else:
            current_value.append(part)
    
    if current_key:
        options[current_key] = ' '.join(current_value)
    
    return options.get(coded_answer, coded_answer)

def generate_patient_name():
    """Generate a random patient name with varied case formatting."""
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
                   'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Taylor']
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    # Apply random case formatting
    case_styles = [
        lambda s: s.upper(),           # JOHN SMITH
        lambda s: s.lower(),           # john smith  
        lambda s: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)), # JoHn SmItH
        lambda s: s                    # John Smith (normal)
    ]
    
    style = random.choice(case_styles)
    return f"{style(first)} {style(last)}"

def find_superlative_respondent(all_respondents, feature, mode='max', filters=None):
    """Find respondent with superlative value for a feature."""
    filtered_respondents = all_respondents
    
    # Apply filters if provided
    if filters:
        for filter_feature, filter_value in filters.items():
            filtered_respondents = [r for r in filtered_respondents 
                                  if r['answers'].get(filter_feature) == filter_value]
    
    if not filtered_respondents:
        return None
        
    # Get numeric values for comparison
    valid_respondents = []
    for resp in filtered_respondents:
        value = resp['answers'].get(feature)
        if value is not None:
            try:
                numeric_value = float(value)
                valid_respondents.append((resp, numeric_value))
            except (ValueError, TypeError):
                # For non-numeric, use original value
                valid_respondents.append((resp, value))
    
    if not valid_respondents:
        return None
    
    # Find superlative
    if mode == 'max':
        return max(valid_respondents, key=lambda x: x[1])[0]
    elif mode == 'min':
        return min(valid_respondents, key=lambda x: x[1])[0]
    
    return None

def calculate_group_average(all_respondents, feature, group_feature, group_value):
    """Calculate average of a feature for a specific group."""
    group_respondents = [r for r in all_respondents 
                        if r['answers'].get(group_feature) == group_value]
    
    values = []
    for resp in group_respondents:
        value = resp['answers'].get(feature)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    return statistics.mean(values) if values else 0

def generate_easy_question(case_id, all_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    templates = [
        # Direct name lookup
        ("direct_name", "What is the {feature} of the patient named '{name}'?"),
        # Superlative lookup
        ("superlative", "What is the {feature} of the {superlative} patient?"),
        # Two-condition lookup
        ("two_condition", "What is the {feature} of the patient with {field_a} = '{value_a}' and {field_b} = '{value_b}'?")
    ]
    
    template_type, template = random.choice(templates)
    feature = random.choice(features)
    
    if template_type == "direct_name":
        # Pick a random respondent
        respondent = random.choice(all_respondents)
        patient_name = generate_patient_name()
        question = template.format(feature=feature.lower(), name=patient_name)
        answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
        return {
            'question': question,
            'answer': answer,
            'selected_feature': feature,
            'target_respondent': respondent['respondent'],
            'patient_name': patient_name,
            'reasoning_complexity': 1
        }
        
    elif template_type == "superlative":
        # Find oldest/youngest for age, highest/lowest for billing
        numeric_features = ['Age', 'Billing Amount']
        if feature in numeric_features:
            superlative = random.choice(['oldest', 'youngest'] if feature == 'Age' else ['highest billing', 'lowest billing'])
            mode = 'max' if 'oldest' in superlative or 'highest' in superlative else 'min'
            respondent = find_superlative_respondent(all_respondents, feature, mode)
            if respondent:
                question = template.format(feature=feature.lower(), superlative=superlative)
                answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
                return {
                    'question': question,
                    'answer': answer,
                    'selected_feature': feature,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 2
                }
        
        # Fallback to direct name
        respondent = random.choice(all_respondents)
        patient_name = generate_patient_name()
        question = f"What is the {feature.lower()} of the patient named '{patient_name}'?"
        answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
        return {
            'question': question,
            'answer': answer,
            'selected_feature': feature,
            'target_respondent': respondent['respondent'],
            'patient_name': patient_name,
            'reasoning_complexity': 1
        }
    
    else:  # two_condition
        # Pick two other features as filters
        other_features = [f for f in features if f != feature]
        if len(other_features) >= 2:
            field_a, field_b = random.sample(other_features, 2)
            # Find a respondent that has values for both filters
            valid_respondents = [r for r in all_respondents 
                               if r['answers'].get(field_a) and r['answers'].get(field_b)]
            if valid_respondents:
                respondent = random.choice(valid_respondents)
                value_a = decode_mcq_answer(field_a, respondent['answers'][field_a], questions_schema)
                value_b = decode_mcq_answer(field_b, respondent['answers'][field_b], questions_schema)
                question = template.format(feature=feature.lower(), field_a=field_a.lower(), 
                                         value_a=value_a, field_b=field_b.lower(), value_b=value_b)
                answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
                return {
                    'question': question,
                    'answer': answer,
                    'selected_feature': feature,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 2
                }
    
    # Fallback
    return generate_easy_question(case_id, all_respondents, features, questions_schema)

def generate_medium_question(case_id, all_respondents, features, questions_schema):
    """Generate Medium mode question (cases 26-40)."""
    templates = [
        ("superlative_with_conditions", "What is the {feature} of the {superlative} patient with {field_a} = '{value_a}' and {field_b} = '{value_b}'?"),
        ("group_superlative", "What is the {feature} of the patient with the {superlative} {numeric_field} among those with {group_field} = '{group_value}'?")
    ]
    
    template_type, template = random.choice(templates)
    feature = random.choice(features)
    
    if template_type == "superlative_with_conditions":
        # Find superlative within a filtered group
        numeric_features = ['Age', 'Billing Amount']
        superlative_feature = random.choice(numeric_features)
        other_features = [f for f in features if f not in [feature, superlative_feature]]
        
        if len(other_features) >= 2:
            field_a, field_b = random.sample(other_features, 2)
            
            # First, find possible values for filters
            possible_values_a = list(set([r['answers'].get(field_a) for r in all_respondents if r['answers'].get(field_a)]))
            possible_values_b = list(set([r['answers'].get(field_b) for r in all_respondents if r['answers'].get(field_b)]))
            
            if possible_values_a and possible_values_b:
                value_a_raw = random.choice(possible_values_a)
                value_b_raw = random.choice(possible_values_b)
                
                # Find superlative respondent with these conditions
                filters = {field_a: value_a_raw, field_b: value_b_raw}
                superlative = 'highest' if random.choice([True, False]) else 'lowest'
                mode = 'max' if superlative == 'highest' else 'min'
                
                respondent = find_superlative_respondent(all_respondents, superlative_feature, mode, filters)
                if respondent:
                    value_a = decode_mcq_answer(field_a, value_a_raw, questions_schema)
                    value_b = decode_mcq_answer(field_b, value_b_raw, questions_schema)
                    
                    question = template.format(
                        feature=feature.lower(), superlative=superlative,
                        field_a=field_a.lower(), value_a=value_a,
                        field_b=field_b.lower(), value_b=value_b
                    )
                    answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
                    return {
                        'question': question,
                        'answer': answer,
                        'selected_feature': feature,
                        'target_respondent': respondent['respondent'],
                        'patient_name': 'N/A',
                        'reasoning_complexity': 4
                    }
    
    elif template_type == "group_superlative":
        # Find superlative within a specific group
        numeric_features = ['Age', 'Billing Amount']
        numeric_field = random.choice(numeric_features)
        categorical_features = [f for f in features if f not in numeric_features and f != feature]
        
        if categorical_features:
            group_field = random.choice(categorical_features)
            possible_group_values = list(set([r['answers'].get(group_field) for r in all_respondents if r['answers'].get(group_field)]))
            
            if possible_group_values:
                group_value_raw = random.choice(possible_group_values)
                filters = {group_field: group_value_raw}
                superlative = 'highest' if random.choice([True, False]) else 'lowest'
                mode = 'max' if superlative == 'highest' else 'min'
                
                respondent = find_superlative_respondent(all_respondents, numeric_field, mode, filters)
                if respondent:
                    group_value = decode_mcq_answer(group_field, group_value_raw, questions_schema)
                    
                    question = template.format(
                        feature=feature.lower(), superlative=superlative,
                        numeric_field=numeric_field.lower(),
                        group_field=group_field.lower(), group_value=group_value
                    )
                    answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
                    return {
                        'question': question,
                        'answer': answer,
                        'selected_feature': feature,
                        'target_respondent': respondent['respondent'],
                        'patient_name': 'N/A',
                        'reasoning_complexity': 3
                    }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, all_respondents, features, questions_schema)

def generate_hard_question(case_id, all_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    template = "What is the {feature} of the patient whose {numeric_field} is the {superlative} above the average {numeric_field} for all patients with {group_field} = '{group_value}'?"
    
    feature = random.choice(features)
    numeric_features = ['Age', 'Billing Amount']
    numeric_field = random.choice(numeric_features)
    categorical_features = [f for f in features if f not in numeric_features and f != feature]
    
    if categorical_features:
        group_field = random.choice(categorical_features)
        possible_group_values = list(set([r['answers'].get(group_field) for r in all_respondents if r['answers'].get(group_field)]))
        
        if possible_group_values:
            group_value_raw = random.choice(possible_group_values)
            
            # Calculate group average
            group_avg = calculate_group_average(all_respondents, numeric_field, group_field, group_value_raw)
            
            # Find respondents in this group whose value is above average
            group_respondents = [r for r in all_respondents 
                               if r['answers'].get(group_field) == group_value_raw]
            
            above_avg_respondents = []
            for resp in group_respondents:
                try:
                    value = float(resp['answers'].get(numeric_field, 0))
                    if value > group_avg:
                        above_avg_respondents.append((resp, value))
                except (ValueError, TypeError):
                    pass
            
            if above_avg_respondents:
                # Find highest among those above average
                superlative = 'highest'
                respondent = max(above_avg_respondents, key=lambda x: x[1])[0]
                
                group_value = decode_mcq_answer(group_field, group_value_raw, questions_schema)
                
                question = template.format(
                    feature=feature.lower(), numeric_field=numeric_field.lower(),
                    superlative=superlative, group_field=group_field.lower(),
                    group_value=group_value
                )
                answer = decode_mcq_answer(feature, respondent['answers'][feature], questions_schema)
                return {
                    'question': question,
                    'answer': answer,
                    'selected_feature': feature,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 5
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, all_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare answer lookup with difficulty modes."""
    
    # Paths
    features_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare-dataset_features.json"
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.csv"
    
    # Load features
    with open(features_file, 'r', encoding='utf-8') as f:
        features_data = json.load(f)
    features = [f for f in features_data['features'] if f != 'respondent']
    print(f"Loaded {len(features)} features")
    
    # Load ALL case data for comprehensive validation
    print("Loading all case data...")
    all_data, questions_schema, all_respondents = load_all_case_data(data_dir)
    print(f"Loaded {len(all_respondents)} total respondents from {len(all_data)} cases")
    
    # Generate Q&A pairs
    qa_pairs = []
    
    for i in range(1, 51):
        case_id = f"case_{i}"
        
        # Determine difficulty mode
        if i <= 25:
            difficulty_mode = "Easy"
            qa_pair = generate_easy_question(case_id, all_respondents, features, questions_schema)
        elif i <= 40:
            difficulty_mode = "Medium" 
            qa_pair = generate_medium_question(case_id, all_respondents, features, questions_schema)
        else:
            difficulty_mode = "Really Hard"
            qa_pair = generate_hard_question(case_id, all_respondents, features, questions_schema)
        
        qa_pair['case_id'] = case_id
        qa_pair['difficulty_mode'] = difficulty_mode
        qa_pairs.append(qa_pair)
        
        print(f"Generated {case_id} ({difficulty_mode}): {qa_pair['question'][:60]}... = '{qa_pair['answer']}'")
    
    # Write to CSV
    fieldnames = ['case_id', 'difficulty_mode', 'question', 'answer', 'selected_feature', 
                  'target_respondent', 'patient_name', 'reasoning_complexity']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qa_pairs)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs with difficulty modes")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    difficulty_counts = {}
    complexity_counts = {}
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        comp = pair['reasoning_complexity']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        complexity_counts[comp] = complexity_counts.get(comp, 0) + 1
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n🧠 Reasoning complexity distribution:")
    for comp, count in sorted(complexity_counts.items()):
        print(f"  Level {comp}: {count} questions")

if __name__ == "__main__":
    main()