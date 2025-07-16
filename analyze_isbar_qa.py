import json
import os
from pathlib import Path

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def analyze_case_data(case_file):
    data = load_json_file(case_file)
    responses = data['responses']
    
    # Collect all possible scores for each metric
    metrics = {
        'Identification': [],
        'Situation': [],
        'Background (history)': [],
        'Background (examination)': [],
        'Assessment': [],
        'Recommendation (clear recommendation)': [],
        'Recommendation (global rating scale)': []
    }
    
    for resp in responses:
        for metric in metrics:
            metrics[metric].append(resp['answers'][metric])
    
    # Find respondents with specific scores
    findings = {
        'perfect_identification': [r['respondent'] for r in responses if r['answers']['Identification'] == 3],
        'good_identification': [r['respondent'] for r in responses if r['answers']['Identification'] >= 2],
        'perfect_situation': [r['respondent'] for r in responses if r['answers']['Situation'] == 3],
        'good_situation': [r['respondent'] for r in responses if r['answers']['Situation'] >= 2],
        'perfect_history': [r['respondent'] for r in responses if r['answers']['Background (history)'] == 3],
        'good_history': [r['respondent'] for r in responses if r['answers']['Background (history)'] >= 2],
        'perfect_examination': [r['respondent'] for r in responses if r['answers']['Background (examination)'] == 3],
        'good_examination': [r['respondent'] for r in responses if r['answers']['Background (examination)'] >= 2],
        'perfect_assessment': [r['respondent'] for r in responses if r['answers']['Assessment'] == 3],
        'good_assessment': [r['respondent'] for r in responses if r['answers']['Assessment'] >= 2],
        'perfect_recommendation': [r['respondent'] for r in responses if r['answers']['Recommendation (clear recommendation)'] == 3],
        'good_recommendation': [r['respondent'] for r in responses if r['answers']['Recommendation (clear recommendation)'] >= 2],
        'perfect_global': [r['respondent'] for r in responses if r['answers']['Recommendation (global rating scale)'] == 3],
        'good_global': [r['respondent'] for r in responses if r['answers']['Recommendation (global rating scale)'] >= 2]
    }
    
    # Filter out empty results
    return {k: sorted(v, key=lambda x: int(x)) for k, v in findings.items() if v}

def generate_qa_pair(case_id, question_type, matching_respondents):
    prompt_template = '''You are a meticulous data analyst AI. Your primary function is to accurately analyze structured data and provide precise, verifiable answers.

You will be given a dataset with two key parts:

A 'questions' section: This is your data dictionary or schema. It is the single source of truth for understanding what each field and score means. Refer to it carefully.

A 'responses' section: This contains the raw data from each individual respondent.

To answer the question correctly, you must first use the 'questions' schema to fully understand the context and meaning of the data points within the 'responses'. Do not rely on any prior knowledge outside of this provided data. Base your entire analysis on the information given.

OUTPUT INSTRUCTIONS:
Provide your final answer directly and concisely. Your output should contain only the answer itself, without explaining your thought process or methodology. For example:

If the question asks for a count, provide only the final number (e.g., "42").

If the question asks for a list of names or IDs, provide them as a simple comma-separated list (e.g., "17, 21, 23").

If the question asks for a specific text comment, provide only that text.

QUESTION:
{question}

DATA:

[Insert the full data block here]'''

    question_map = {
        'perfect_identification': 'Find all respondents with perfect identification scores (3).',
        'good_identification': 'Find all respondents with good or perfect identification scores (2-3).',
        'perfect_situation': 'Find all respondents with perfect situation scores (3).',
        'good_situation': 'Find all respondents with good or perfect situation scores (2-3).',
        'perfect_history': 'Find all respondents with perfect background history scores (3).',
        'good_history': 'Find all respondents with good or perfect background history scores (2-3).',
        'perfect_examination': 'Find all respondents with perfect background examination scores (3).',
        'good_examination': 'Find all respondents with good or perfect background examination scores (2-3).',
        'perfect_assessment': 'Find all respondents with perfect assessment scores (3).',
        'good_assessment': 'Find all respondents with good or perfect assessment scores (2-3).',
        'perfect_recommendation': 'Find all respondents with perfect recommendation scores (3).',
        'good_recommendation': 'Find all respondents with good or perfect recommendation scores (2-3).',
        'perfect_global': 'Find all respondents with perfect global rating scores (3).',
        'good_global': 'Find all respondents with good or perfect global rating scores (2-3).'
    }

    return {
        'case_id': case_id,
        'task': 'rule_based_querying',
        'prompt': prompt_template.format(question=question_map[question_type]),
        'expected_answer': ', '.join(matching_respondents),
        'metadata': {
            'rule_description': question_map[question_type],
            'matching_respondents': matching_respondents,
            'question_category': question_type
        }
    }

def main():
    # Paths
    cases_dir = Path('benchmark_cache/isbar/rule_based_querying/json')
    qa_pairs_file = Path('prompts/isbar/isbar_rule_based_querying_qa_pairs.json')
    
    # Analyze all cases
    all_cases = {}
    for case_file in cases_dir.glob('case_*.json'):
        case_id = case_file.stem
        findings = analyze_case_data(case_file)
        if findings:  # Only store cases with valid findings
            all_cases[case_id] = findings
    
    # Generate new QA pairs
    new_qa_pairs = []
    for case_id, findings in all_cases.items():
        # Pick the finding with the most respondents to create a question
        best_finding = max(findings.items(), key=lambda x: len(x[1]))
        new_qa_pairs.append(generate_qa_pair(case_id, best_finding[0], best_finding[1]))
    
    # Sort by case_id
    new_qa_pairs.sort(key=lambda x: int(x['case_id'].split('_')[1]))
    
    # Save the new QA pairs
    save_json_file(qa_pairs_file, new_qa_pairs)

if __name__ == '__main__':
    main() 