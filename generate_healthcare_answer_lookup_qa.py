#!/usr/bin/env python3
import json
import csv
import random
import os
from pathlib import Path

def load_features(features_file):
    """Load feature definitions from JSON file."""
    with open(features_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Exclude 'respondent' as it's not a queryable feature for answer lookup
    features = [f for f in data['features'] if f != 'respondent']
    return features

def load_case_data(case_file):
    """Load data from a specific case JSON file."""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def decode_mcq_answer(feature, coded_answer, questions_schema):
    """Decode MCQ answer from letter code to human-readable text."""
    question_text = questions_schema[feature]
    
    if '[MCQ:' not in question_text:
        # Not an MCQ, return as-is
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
            # This is a key like "A."
            if current_key:
                options[current_key] = ' '.join(current_value)
            current_key = part[0]
            current_value = []
        else:
            current_value.append(part)
    
    # Add the last option
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

def generate_question_answer_pair(case_id, case_data, selected_feature):
    """Generate a question-answer pair for a specific case and feature."""
    questions_schema = case_data['questions']
    responses = case_data['responses']
    
    # Randomly select a respondent
    selected_respondent = random.choice(responses)
    respondent_id = selected_respondent['respondent']
    
    # Get the raw answer
    raw_answer = selected_respondent['answers'][selected_feature]
    
    # Decode the answer if it's MCQ
    decoded_answer = decode_mcq_answer(selected_feature, raw_answer, questions_schema)
    
    # Generate patient name
    patient_name = generate_patient_name()
    
    # Create the question
    question = f"What is the {selected_feature.lower()} for {patient_name}?"
    
    return {
        'case_id': case_id,
        'question': question,
        'answer': decoded_answer,
        'selected_feature': selected_feature,
        'target_respondent': respondent_id,
        'patient_name': patient_name,
        'raw_answer': raw_answer
    }

def main():
    """Generate 50 question-answer pairs for healthcare answer lookup task."""
    
    # Paths
    features_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare-dataset_features.json"
    data_dir = "/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/healthcare-dataset/answer_lookup/json"
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.csv"
    
    # Load features
    features = load_features(features_file)
    print(f"Loaded {len(features)} features: {features}")
    
    # Generate Q&A pairs
    qa_pairs = []
    
    for i in range(1, 51):  # case_1 to case_50
        case_file = os.path.join(data_dir, f"case_{i}.json")
        
        if not os.path.exists(case_file):
            print(f"Warning: {case_file} not found, skipping...")
            continue
            
        # Load case data
        case_data = load_case_data(case_file)
        
        # Randomly select a feature for this case
        selected_feature = random.choice(features)
        
        # Generate Q&A pair
        qa_pair = generate_question_answer_pair(f"case_{i}", case_data, selected_feature)
        qa_pairs.append(qa_pair)
        
        print(f"Generated case_{i}: {selected_feature} -> '{qa_pair['question']}' = '{qa_pair['answer']}'")
    
    # Write to CSV
    fieldnames = ['case_id', 'question', 'answer', 'selected_feature', 'target_respondent', 'patient_name', 'raw_answer']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qa_pairs)
    
    print(f"\n✅ Successfully generated {len(qa_pairs)} Q&A pairs")
    print(f"📁 Output saved to: {output_file}")
    
    # Summary statistics
    feature_counts = {}
    for pair in qa_pairs:
        feature = pair['selected_feature']
        feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    print(f"\n📊 Feature distribution:")
    for feature, count in sorted(feature_counts.items()):
        print(f"  {feature}: {count} questions")

if __name__ == "__main__":
    main()