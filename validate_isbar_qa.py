import json
import os
import glob
from pathlib import Path

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_qa_pairs(task_name):
    print(f"\nValidating {task_name}...")
    
    # Load QA pairs
    qa_pairs_file = f"prompts/isbar/isbar_{task_name}_qa_pairs.json"
    qa_pairs = load_json_file(qa_pairs_file)
    
    # Get all case files from json subdirectory
    case_files = glob.glob(f"benchmark_cache/isbar/{task_name}/json/case_*.json")
    if not case_files:
        print(f"ERROR: No case files found in benchmark_cache/isbar/{task_name}/json/")
        return
        
    case_files.sort()
    print(f"Found {len(case_files)} case files")
    
    all_case_data = {}
    for case_file in case_files:
        case_data = load_json_file(case_file)
        case_num = int(Path(case_file).stem.split('_')[1])
        all_case_data[case_num] = case_data

    # Validate each QA pair
    for qa_pair in qa_pairs:
        case_id = qa_pair.get('case_id')
        if not case_id:
            print(f"ERROR: Missing case_id in QA pair")
            continue
            
        try:
            case_num = int(case_id.split('_')[1])
        except (IndexError, ValueError):
            print(f"ERROR: Invalid case_id format: {case_id}")
            continue
            
        question = qa_pair.get('prompt', '')
        answer = qa_pair.get('expected_answer')
        
        if case_num not in all_case_data:
            print(f"ERROR: Case {case_num} not found in data")
            continue
            
        case_data = all_case_data[case_num]
        
        # Extract all scores for validation
        scores = {
            'identification': [r['answers'].get('Identification') for r in case_data.get('responses', [])],
            'situation': [r['answers'].get('Situation') for r in case_data.get('responses', [])],
            'background': [r['answers'].get('Background (history)') for r in case_data.get('responses', [])],
            'assessment': [r['answers'].get('Assessment') for r in case_data.get('responses', [])],
            'recommendation': [r['answers'].get('Recommendation (clear recommendation)') for r in case_data.get('responses', [])],
            'global_rating': [r['answers'].get('Recommendation (global rating scale)') for r in case_data.get('responses', [])]
        }
        
        # Convert answer to list of integers if it's a string of numbers
        if isinstance(answer, str) and answer.replace(',', '').replace(' ', '').isdigit():
            answer = [int(x.strip()) for x in answer.split(',')]
        
        # Validate answer exists in respondent IDs
        if isinstance(answer, list):
            respondent_ids = [r.get('respondent') for r in case_data.get('responses', [])]
            print(f"\nCase {case_num}:")
            print(f"Question: {question}")
            print(f"Expected answer: {answer}")
            print(f"Available respondents: {respondent_ids}")
            print(f"Scores:")
            for key, values in scores.items():
                print(f"  {key}: {values}")
            
            for ans in answer:
                if str(ans) not in respondent_ids:
                    print(f"ERROR in case {case_num}: Answer {ans} not in respondent IDs {respondent_ids}")
                    print(f"Question: {question}")
                    print(f"Full answer: {answer}")
        
        # Special validation for score-related questions
        if "perfect score" in question.lower() or "highest score" in question.lower():
            score_type = None
            for key in scores.keys():
                if key in question.lower():
                    score_type = key
                    break
            
            if score_type:
                max_score = max(scores[score_type])
                perfect_respondents = [r.get('respondent') for r in case_data.get('responses', []) 
                                    if r['answers'].get(score_type.title()) == max_score]
                if sorted([str(x) for x in answer]) != sorted(perfect_respondents):
                    print(f"ERROR in case {case_num}: Perfect {score_type} score answer mismatch")
                    print(f"Question: {question}")
                    print(f"Given answer: {answer}")
                    print(f"Correct answer should be: {perfect_respondents}")
        
        # Validate good/perfect score questions
        if "good or perfect" in question.lower():
            score_type = None
            for key in scores.keys():
                if key in question.lower():
                    score_type = key
                    break
                    
            if score_type:
                good_respondents = [r.get('respondent') for r in case_data.get('responses', [])
                                 if r['answers'].get(score_type.title()) >= 2]
                if sorted([str(x) for x in answer]) != sorted(good_respondents):
                    print(f"ERROR in case {case_num}: Good/perfect {score_type} score answer mismatch")
                    print(f"Question: {question}")
                    print(f"Given answer: {answer}")
                    print(f"Correct answer should be: {good_respondents}")

# Validate all tasks
tasks = [
    "rule_based_querying",
    "answer_lookup",
    "answer_reverse_lookup",
    "respondent_count",
    "multi_hop_relational_inference",
    "conceptual_aggregation"
]

for task in tasks:
    validate_qa_pairs(task) 