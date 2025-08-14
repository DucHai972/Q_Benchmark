# Question and Answer Design Plan for Q_Benchmark

## Overview

This document outlines the plan for designing questions and answers for our benchmark tasks across 5 datasets and 6 task types with varying difficulty modes.

## Key Requirements

1. **Complete Data Retrieval**: When asking about feature X, retrieve ALL respondents and their feature X values FROM THAT SPECIFIC CASE to ensure answer accuracy and handle multiple matches.

2. **Difficulty Modes**: 
   - Cases 1-25: Easy Mode 
   - Cases 26-40: Medium Mode
   - Cases 41-50: Really Hard Mode

## File Structure and Information Sources

### Question Format Templates
Each dataset has its own question format files for each task:
- `questions_design/{dataset}/question_format_{task}.md`

Examples:
- `questions_design/healthcare-dataset/question_format_answer_lookup.md`
- `questions_design/healthcare-dataset/question_format_answer_reverse_lookup.md`
- `questions_design/isbar/question_format_conceptual_aggregation.md`
- `questions_design/self-reported-mental-health/question_format_multi_hop_relational_inference.md`
- etc.

### Feature Definitions
- **Healthcare**: `questions_design/healthcare-dataset/healthcare-dataset_features.json`
- **ISBAR**: `questions_design/isbar/isbar_features.json`
- **Mental Health**: `questions_design/self-reported-mental-health/self-reported-mental-health_features.json`
- **Stack Overflow**: `questions_design/stack-overflow-2022/stack-overflow-2022_features.json`
- **SUS-UTA7**: `questions_design/sus-uta7/sus-uta7_features.json`

### Source Data
- **Path Pattern**: `benchmark_cache/{dataset}/{task}/json/case_{X}.json`
- **Requirement**: Load ALL case files for complete validation

## Task Types

All 6 task types use difficulty modes:

1. **Answer Lookup**: Varies by difficulty mode
2. **Answer Reverse Lookup**: Varies by difficulty mode
3. **Conceptual Aggregation**: Varies by difficulty mode
4. **Multi-hop Relational Inference**: Varies by difficulty mode
5. **Respondent Count**: Varies by difficulty mode
6. **Rule-based Querying**: Varies by difficulty mode

## JSON Output Structure

Each generated JSON file contains an array of question objects with:
- `case_id`: case_1 to case_50
- `difficulty_mode`: Easy/Medium/Really Hard
- `question`: Generated question text
- `answer`: Ground truth answer
- `selected_features`: Array of all features used in the question
- `target_respondent`: Specific respondent ID referenced
- `patient_name`: Generated patient name (if applicable)
- `reasoning_complexity`: Number of conditions/calculations required
- `feature_values`: Object containing all relevant feature values from all respondents
- `calculation_details`: Object containing intermediate calculations (averages, filters, etc.)

## Implementation Steps

1. Read question format from `question_format_{task}.md`
2. Load features from `{dataset}_features.json`
3. For each case (case_1 to case_50):
   - Load ONLY that specific case from `benchmark_cache/{dataset}/{task}/json/case_X.json`
   - Determine features needed based on difficulty mode
   - Extract ALL chosen features from ALL respondents IN THAT CASE
   - Store complete feature-value mappings for ground truth validation within that case
   - Calculate intermediate values (averages, filters, superlatives) within that case
   - Generate question and validate answer
5. Output to `questions_design/{dataset}/{dataset}_{task}_qa.json`

## Key Features of JSON Output

1. **Multiple Feature Support**: Each question stores all selected features used
2. **Complete Feature Values**: All respondents' values for chosen features included  
3. **Calculation Details**: Intermediate calculations, statistics, and reasoning steps
4. **Ground Truth Validation**: Comprehensive validation against complete dataset

## Success Criteria

- 50 questions per dataset-task combination
- Multiple features for Medium/Hard questions (2-4 features per question)
- Proper difficulty progression: Easy (1-25), Medium (26-40), Hard (41-50) 
- Complete data validation against ALL respondents for chosen features
- Detailed calculation tracking for complex statistical operations
- Zero ambiguous answers with full reasoning transparency