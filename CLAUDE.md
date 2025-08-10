# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Q-Benchmark is an LLM evaluation framework that tests language model performance across different data formats. It evaluates how well LLMs can understand and query structured data presented in various formats (JSON, XML, HTML, Markdown, TXT, TTL) across multiple benchmark tasks.

## Key Commands

### Running Benchmarks
```bash
# Basic benchmark with default settings (healthcare dataset, answer_lookup task, 5 cases)
python benchmark_pipeline.py

# Run comprehensive benchmark on all datasets and tasks
python benchmark_pipeline.py --dataset all --task all --format all --max-cases 50

# Test specific models
python benchmark_pipeline.py --model openai --dataset all --task all --format all --max-cases 50
python benchmark_pipeline.py --model google --dataset all --task all --format all --max-cases 50

# Run with specific parameters
python benchmark_pipeline.py --dataset healthcare-dataset --task answer_lookup --format json --max-cases 10

# Run with prompt variants (new feature!)
python benchmark_pipeline.py --variants wo_role_prompting --dataset healthcare-dataset --task answer_lookup --format json
python benchmark_pipeline.py --variants wo_oneshot --model openai --format all --max-cases 20
python benchmark_pipeline.py --variants wo_format_explaination --dataset all --task all --format json

# Available variants:
# - wo_role_prompting: Remove role prompting sections
# - wo_partition_mark: Remove structural partition marks  
# - wo_format_explaination: Remove format explanation sections
# - wo_oneshot: Remove one-shot examples
# - wo_change_order: Move questionnaire to end of prompt

# Results saved to benchmark_results/modelname_variants/ when using variants
# Results saved to benchmark_results/modelname/ when using standard prompts

# List available options
python benchmark_pipeline.py --list
python benchmark_pipeline.py --variants wo_role_prompting --list
```

### Environment Setup
```bash
# Create .env file with API keys (required)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Run tests with verbose output for debugging
python main.py --verbose --cases 1 --output debug_run
```

## Architecture Overview

### Core Components

1. **main.py** - CLI entry point with argument parsing and benchmark orchestration
2. **benchmark_pipeline.py** - Main pipeline orchestrating the benchmark execution
3. **llm_clients.py** - API clients for OpenAI, Google Gemini, and DeepSeek models
4. **benchmark_prompt_generator.py** - Generates benchmark prompts by combining templates with data
5. **configurable_benchmark_runner.py** - Advanced configurable benchmark runner with prompt variations

### Data Structure

- **preprocessed_data/** - Contains datasets in multiple formats (JSON, XML, HTML, MD, TXT, TTL)
- **prompts/** - Basic prompt templates for benchmark tasks
- **advanced_prompts/** - Advanced template-based prompts with configurable options
- **benchmark_cache/** - Cached benchmark data for faster execution
- **benchmark_results/** - Output directory containing timestamped benchmark runs

### Benchmark Tasks

The framework supports 6 core benchmark tasks:
- `answer_lookup` - Direct answer retrieval from data
- `answer_reverse_lookup` - Finding questions for given answers
- `conceptual_aggregation` - Grouping and summarizing concepts
- `multi_hop_relational_inference` - Complex multi-step reasoning
- `respondent_count` - Counting specific data points
- `rule_based_querying` - Query execution following specific rules

### Supported Models

- **OpenAI**: gpt-3.5-turbo
- **Google**: gemini-1.5-flash  
- **DeepSeek**: deepseek-chat

### Data Formats

All datasets are available in 6 formats: JSON, XML, HTML, Markdown, TXT, TTL (Turtle/RDF)

## Key Implementation Notes

### Missing Dependencies
- The codebase references `evaluator.py` containing `BenchmarkEvaluator` class, but this file is missing
- No requirements.txt or dependency management files are present
- Required Python packages based on imports: `openai`, `google-generativeai`, `pandas`, `openpyxl`, `tqdm`, `python-dotenv`

### Output Structure
```
benchmark_results/
└── run_YYYYMMDD_HHMMSS/
    ├── summary.json                    # Overall statistics
    ├── benchmark_results_table.xlsx    # Results table (correct/total)
    ├── benchmark_scores_table.xlsx     # Scores table (score/total)
    └── [dataset]/
        └── [task]/
            └── [model]_results.json    # Detailed results
```

### Rate Limiting
- Built-in 0.5 second delay between API calls to avoid rate limits
- Progress bars show real-time execution status

### Configuration Options
The framework supports various prompt configurations:
- One-shot examples
- Role prompting
- Format explanations
- Data positioning (beginning vs end)
- Partition markers

## Development Workflow

1. **Setup**: Create `.env` file with API keys
2. **Quick Test**: `python main.py --cases 1 --formats json` 
3. **Full Development**: Use `--verbose` flag for detailed logging
4. **Scale Up**: Gradually increase `--cases` and add more formats/datasets
5. **Production**: Run comprehensive benchmarks with meaningful `--output` names

## Important Files to Create

If extending the framework, you may need to create:
- `evaluator.py` - Contains the missing `BenchmarkEvaluator` class
- `requirements.txt` - Python dependencies
- Test files for validation

## Data Flow

1. **Prompt Generation**: Templates + Data → Formatted prompts
2. **LLM Evaluation**: Prompts → Model responses  
3. **Scoring**: Responses + Expected answers → Scores
4. **Aggregation**: Individual results → Summary statistics and Excel reports