#!/usr/bin/env python3
import json
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

def extract_feature_values(all_respondents, features):
    """Extract all chosen features from all respondents."""
    feature_values = {}
    
    for feature in features:
        feature_values[feature] = {}
        for resp in all_respondents:
            respondent_id = resp['respondent']
            raw_value = resp['answers'].get(feature)
            feature_values[feature][respondent_id] = raw_value
    
    return feature_values

def find_superlative_respondent(all_respondents, feature, mode='max', filters=None):
    """Find respondent with superlative value for a feature."""
    filtered_respondents = all_respondents
    
    # Apply filters if provided
    if filters:
        for filter_feature, filter_value in filters.items():
            filtered_respondents = [r for r in filtered_respondents 
                                  if r['answers'].get(filter_feature) == filter_value]
    
    if not filtered_respondents:
        return None, None
        
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
        return None, None
    
    # Find superlative
    if mode == 'max':
        result = max(valid_respondents, key=lambda x: x[1])
    elif mode == 'min':
        result = min(valid_respondents, key=lambda x: x[1])
    else:
        result = valid_respondents[0]
    
    return result[0], result[1]

def calculate_group_statistics(all_respondents, feature, group_feature, group_value):
    """Calculate statistics for a feature within a specific group."""
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
    
    if not values:
        return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
    
    return {
        'count': len(values),
        'average': statistics.mean(values),
        'min': min(values),
        'max': max(values)
    }

def generate_patient_name():
    """Generate a random patient name with varied case formatting."""
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
                   'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Taylor']
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    case_styles = [
        lambda s: s.upper(),           # JOHN SMITH
        lambda s: s.lower(),           # john smith  
        lambda s: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)), # JoHn SmItH
        lambda s: s                    # John Smith (normal)
    ]
    
    style = random.choice(case_styles)
    return f"{style(first)} {style(last)}"

def generate_easy_question(case_id, all_respondents, features, questions_schema):
    """Generate Easy mode question (cases 1-25)."""
    templates = [
        ("direct_name", "What is the {feature} of the patient named '{name}'?"),
        ("superlative", "What is the {feature} of the {superlative} patient?"),
        ("two_condition", "What is the {feature} of the patient with {field_a} = '{value_a}' and {field_b} = '{value_b}'?")
    ]
    
    template_type, template = random.choice(templates)
    target_feature = random.choice(features)
    selected_features = [target_feature]
    
    if template_type == "direct_name":
        # Pick a random respondent
        respondent = random.choice(all_respondents)
        patient_name = generate_patient_name()
        question = template.format(feature=target_feature.lower(), name=patient_name)
        answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
        
        feature_values = extract_feature_values(all_respondents, selected_features)
        
        return {
            'case_id': case_id,
            'difficulty_mode': "Easy",
            'question': question,
            'answer': answer,
            'selected_features': selected_features,
            'target_respondent': respondent['respondent'],
            'patient_name': patient_name,
            'reasoning_complexity': 1,
            'feature_values': feature_values,
            'calculation_details': {
                'method': 'direct_lookup',
                'target_value': respondent['answers'][target_feature]
            }
        }
        
    elif template_type == "superlative":
        # Find oldest/youngest for age, highest/lowest for billing
        numeric_features = ['Age', 'Billing Amount']
        if target_feature in numeric_features:
            superlative = random.choice(['oldest', 'youngest'] if target_feature == 'Age' else ['highest billing', 'lowest billing'])
            mode = 'max' if 'oldest' in superlative or 'highest' in superlative else 'min'
            respondent, superlative_value = find_superlative_respondent(all_respondents, target_feature, mode)
            
            if respondent:
                question = template.format(feature=target_feature.lower(), superlative=superlative)
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(all_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'calculation_details': {
                        'method': 'superlative',
                        'superlative_type': mode,
                        'superlative_value': superlative_value,
                        'all_values': [float(v) for v in feature_values[target_feature].values() if v and str(v).replace('.', '').replace('-', '').isdigit()]
                    }
                }
        
        # Fallback to direct name
        return generate_easy_question(case_id, all_respondents, features, questions_schema)
    
    else:  # two_condition
        # Pick two other features as filters
        other_features = [f for f in features if f != target_feature]
        if len(other_features) >= 2:
            field_a, field_b = random.sample(other_features, 2)
            selected_features = [target_feature, field_a, field_b]
            
            # Find a respondent that has values for both filters
            valid_respondents = [r for r in all_respondents 
                               if r['answers'].get(field_a) and r['answers'].get(field_b)]
            if valid_respondents:
                respondent = random.choice(valid_respondents)
                value_a = decode_mcq_answer(field_a, respondent['answers'][field_a], questions_schema)
                value_b = decode_mcq_answer(field_b, respondent['answers'][field_b], questions_schema)
                question = template.format(feature=target_feature.lower(), field_a=field_a.lower(), 
                                         value_a=value_a, field_b=field_b.lower(), value_b=value_b)
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(all_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Easy",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 2,
                    'feature_values': feature_values,
                    'calculation_details': {
                        'method': 'two_condition_filter',
                        'filter_conditions': {
                            field_a: {'raw': respondent['answers'][field_a], 'decoded': value_a},
                            field_b: {'raw': respondent['answers'][field_b], 'decoded': value_b}
                        }
                    }
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
    target_feature = random.choice(features)
    
    if template_type == "superlative_with_conditions":
        # Find superlative within a filtered group
        numeric_features = ['Age', 'Billing Amount']
        superlative_feature = random.choice(numeric_features)
        other_features = [f for f in features if f not in [target_feature, superlative_feature]]
        
        if len(other_features) >= 2:
            field_a, field_b = random.sample(other_features, 2)
            selected_features = [target_feature, superlative_feature, field_a, field_b]
            
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
                
                respondent, superlative_value = find_superlative_respondent(all_respondents, superlative_feature, mode, filters)
                if respondent:
                    value_a = decode_mcq_answer(field_a, value_a_raw, questions_schema)
                    value_b = decode_mcq_answer(field_b, value_b_raw, questions_schema)
                    
                    question = template.format(
                        feature=target_feature.lower(), superlative=superlative,
                        field_a=field_a.lower(), value_a=value_a,
                        field_b=field_b.lower(), value_b=value_b
                    )
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(all_respondents, selected_features)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'patient_name': 'N/A',
                        'reasoning_complexity': 4,
                        'feature_values': feature_values,
                        'calculation_details': {
                            'method': 'filtered_superlative',
                            'superlative_feature': superlative_feature,
                            'superlative_type': mode,
                            'superlative_value': superlative_value,
                            'filter_conditions': {
                                field_a: {'raw': value_a_raw, 'decoded': value_a},
                                field_b: {'raw': value_b_raw, 'decoded': value_b}
                            },
                            'filtered_group_size': len([r for r in all_respondents if r['answers'].get(field_a) == value_a_raw and r['answers'].get(field_b) == value_b_raw])
                        }
                    }
    
    elif template_type == "group_superlative":
        # Find superlative within a specific group
        numeric_features = ['Age', 'Billing Amount']
        numeric_field = random.choice(numeric_features)
        categorical_features = [f for f in features if f not in numeric_features and f != target_feature]
        
        if categorical_features:
            group_field = random.choice(categorical_features)
            selected_features = [target_feature, numeric_field, group_field]
            
            possible_group_values = list(set([r['answers'].get(group_field) for r in all_respondents if r['answers'].get(group_field)]))
            
            if possible_group_values:
                group_value_raw = random.choice(possible_group_values)
                filters = {group_field: group_value_raw}
                superlative = 'highest' if random.choice([True, False]) else 'lowest'
                mode = 'max' if superlative == 'highest' else 'min'
                
                respondent, superlative_value = find_superlative_respondent(all_respondents, numeric_field, mode, filters)
                if respondent:
                    group_value = decode_mcq_answer(group_field, group_value_raw, questions_schema)
                    
                    question = template.format(
                        feature=target_feature.lower(), superlative=superlative,
                        numeric_field=numeric_field.lower(),
                        group_field=group_field.lower(), group_value=group_value
                    )
                    answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                    
                    feature_values = extract_feature_values(all_respondents, selected_features)
                    group_stats = calculate_group_statistics(all_respondents, numeric_field, group_field, group_value_raw)
                    
                    return {
                        'case_id': case_id,
                        'difficulty_mode': "Medium",
                        'question': question,
                        'answer': answer,
                        'selected_features': selected_features,
                        'target_respondent': respondent['respondent'],
                        'patient_name': 'N/A',
                        'reasoning_complexity': 3,
                        'feature_values': feature_values,
                        'calculation_details': {
                            'method': 'group_superlative',
                            'numeric_field': numeric_field,
                            'superlative_type': mode,
                            'superlative_value': superlative_value,
                            'group_field': group_field,
                            'group_value': {'raw': group_value_raw, 'decoded': group_value},
                            'group_statistics': group_stats
                        }
                    }
    
    # Fallback to easy mode
    return generate_easy_question(case_id, all_respondents, features, questions_schema)

def generate_hard_question(case_id, all_respondents, features, questions_schema):
    """Generate Really Hard mode question (cases 41-50)."""
    template = "What is the {feature} of the patient whose {numeric_field} is the {superlative} above the average {numeric_field} for all patients with {group_field} = '{group_value}'?"
    
    target_feature = random.choice(features)
    numeric_features = ['Age', 'Billing Amount']
    numeric_field = random.choice(numeric_features)
    categorical_features = [f for f in features if f not in numeric_features and f != target_feature]
    
    if categorical_features:
        group_field = random.choice(categorical_features)
        selected_features = [target_feature, numeric_field, group_field]
        
        possible_group_values = list(set([r['answers'].get(group_field) for r in all_respondents if r['answers'].get(group_field)]))
        
        if possible_group_values:
            group_value_raw = random.choice(possible_group_values)
            
            # Calculate group statistics
            group_stats = calculate_group_statistics(all_respondents, numeric_field, group_field, group_value_raw)
            group_avg = group_stats['average']
            
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
                superlative_value = max(above_avg_respondents, key=lambda x: x[1])[1]
                
                group_value = decode_mcq_answer(group_field, group_value_raw, questions_schema)
                
                question = template.format(
                    feature=target_feature.lower(), numeric_field=numeric_field.lower(),
                    superlative=superlative, group_field=group_field.lower(),
                    group_value=group_value
                )
                answer = decode_mcq_answer(target_feature, respondent['answers'][target_feature], questions_schema)
                
                feature_values = extract_feature_values(all_respondents, selected_features)
                
                return {
                    'case_id': case_id,
                    'difficulty_mode': "Really Hard",
                    'question': question,
                    'answer': answer,
                    'selected_features': selected_features,
                    'target_respondent': respondent['respondent'],
                    'patient_name': 'N/A',
                    'reasoning_complexity': 5,
                    'feature_values': feature_values,
                    'calculation_details': {
                        'method': 'above_average_superlative',
                        'numeric_field': numeric_field,
                        'group_field': group_field,
                        'group_value': {'raw': group_value_raw, 'decoded': group_value},
                        'group_statistics': group_stats,
                        'above_average_threshold': group_avg,
                        'above_average_candidates': len(above_avg_respondents),
                        'superlative_value': superlative_value
                    }
                }
    
    # Fallback to medium mode
    return generate_medium_question(case_id, all_respondents, features, questions_schema)

def main():
    """Generate 50 question-answer pairs for healthcare answer lookup with difficulty modes in JSON format."""
    
    # Paths
    features_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare-dataset_features.json"
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.json"
    
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
        
        # Determine difficulty mode and generate question
        if i <= 25:
            qa_pair = generate_easy_question(case_id, all_respondents, features, questions_schema)
        elif i <= 40:
            qa_pair = generate_medium_question(case_id, all_respondents, features, questions_schema)
        else:
            qa_pair = generate_hard_question(case_id, all_respondents, features, questions_schema)
        
        qa_pairs.append(qa_pair)
        
        print(f"Generated {case_id} ({qa_pair['difficulty_mode']}): Features: {qa_pair['selected_features']} -> '{qa_pair['answer']}'")
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs with multiple features")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    difficulty_counts = {}
    feature_usage = {}
    
    for pair in qa_pairs:
        diff = pair['difficulty_mode']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        # Count feature usage
        for feature in pair['selected_features']:
            feature_usage[feature] = feature_usage.get(feature, 0) + 1
    
    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count} questions")
    
    print(f"\n🎯 Feature usage distribution:")
    for feature, count in sorted(feature_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {count} times")

if __name__ == "__main__":
    main()