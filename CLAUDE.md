# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Q_Benchmark is a comprehensive benchmark system for evaluating large language model performance on structured data question-answering tasks. The system tests different data formats (JSON, XML, HTML, Markdown, TTL, TXT) across various question types and datasets.

## Key Commands

### Virtual Environment Setup
```bash
cd ~/Q_Benchmark && source ~/Q_Benchmark/.venv/bin/activate
```

### Running Benchmarks
```bash
# Run single benchmark
python3 benchmark_pipeline.py --model openai --openai-model gpt-4.1-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 2

# Run full benchmark (all datasets/tasks/formats)
python benchmark_pipeline.py --model openai --openai-model gpt-5-mini

# Run with variants (prompt ablations)
python benchmark_pipeline.py --model google --google-model gemini-2.5-flash --variants all

# Run with self-augmentation
python benchmark_pipeline.py --model openai --openai-model gpt-4.1-mini --self_aug format_explaination

# List available options
python benchmark_pipeline.py --list
```

### Analysis Commands
```bash
# Analyze results for specific model
python benchmark_analysis.py --model gpt-4.1-mini

# Analyze all variants
python benchmark_analysis.py --variants all --model gpt-4.1-mini

# List available models and variants
python benchmark_analysis.py --list
```

## Architecture

### Core Components

- **benchmark_pipeline.py**: Main execution engine that runs LLM evaluations
  - Supports OpenAI and Google Gemini models
  - Handles prompt variants and self-augmentation techniques
  - Manages rate limiting and error handling
  - Saves results with smart merging capabilities

- **benchmark_analysis.py**: Results analysis and reporting system
  - Generates accuracy tables by format and task
  - Creates summary statistics and CSV exports
  - Supports variant comparison analysis

### Data Structure

1. **preprocessed_data/**: Original datasets in multiple formats (JSON, XML, HTML, MD, TTL, TXT)
   - Each dataset contains structured questionnaire data with questions schema and response data

2. **prompts/**: Base prompt templates for each task type
   - 6 task types: answer_lookup, answer_reverse_lookup, conceptual_aggregation, multi_hop_relational_inference, respondent_count, rule_based_querying

3. **converted_prompts/**: Generated prompts combining templates with data formats
   - Organized by dataset/task/format structure
   - CSV files with case_id, task, question, questionnaire, expected_answer, prompt columns

4. **converted_prompts_variants/**: Prompt ablation studies
   - wo_role_prompting, wo_partition_mark, wo_format_explaination, wo_oneshot, wo_change_order

5. **converted_prompts_self_aug/**: Self-augmentation prompts with [REQUEST] placeholders

6. **benchmark_results/**: LLM responses and evaluations
   - Organized by model name directories
   - Contains Response and Correct columns added to CSV files

7. **analysis_results/**: Summary statistics and accuracy tables

### Configuration

- **API Keys**: Set in `.env` file (see `.env.example`)
  - `OPENAI_API_KEY` for OpenAI models
  - `GOOGLE_API_KEY` for Google Gemini models

- **Datasets**: 5 datasets available
  - healthcare-dataset, isbar, self-reported-mental-health, stack-overflow-2022, sus-uta7

### Task Types

1. **answer_lookup**: Find specific values for named entities
2. **answer_reverse_lookup**: Find entities with specific attribute values  
3. **conceptual_aggregation**: Count entities meeting criteria
4. **multi_hop_relational_inference**: Complex multi-step reasoning
5. **respondent_count**: Count total respondents
6. **rule_based_querying**: Apply logical rules to data

### Evaluation

Simple substring matching evaluation - checks if expected answer appears in LLM response (case-insensitive). Results stored as True/False in Correct column.

## Development Notes

- The system uses smart merging when saving results - existing case_ids are updated, new ones are added
- Rate limiting (0.5s delay) is implemented to respect API limits
- Results are organized by model name with variant suffixes (e.g., "gpt-4.1-mini_wo_role_prompting")
- All file paths use forward slashes and support multiple data formats seamlessly
- The CLI provides comprehensive progress tracking with tqdm progress bars when available