# Q-Benchmark CLI Tutorial

Welcome to the Q-Benchmark CLI! This tutorial will guide you through using the command-line interface to evaluate LLM performance across different data formats.

python main.py --model openai --datasets all --tasks all --formats all --cases 50 --output benchmark_openai

python main.py --model google --datasets all --tasks all --formats all --cases 50 --output benchmark_google

python main.py --model deepseek --datasets all --tasks all --formats all --cases 50 --output benchmark_deepseeks




## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Command Reference](#command-reference)
4. [Examples](#examples)
5. [Understanding Output](#understanding-output)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### 1. Environment Setup
Make sure you have Python 3.7+ installed and the virtual environment activated:

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate
```

### 2. API Keys Configuration
Create a `.env` file in the project root with your API keys:

```bash
# Required: At least one API key
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**Note**: You need at least one API key. The benchmark will automatically detect and use available models based on your API keys.

## 🚀 Quick Start

### Basic Usage
The simplest way to run a benchmark:

```bash
python main.py
```

This runs with default settings:
- Dataset: `healthcare-dataset`
- Task: `answer_lookup`
- Cases: 5 per format
- Formats: JSON and XML
- Output: `benchmark_results/run_timestamp/`
- Generates Excel report
- **Progress bars** show real-time execution status

### Help Command
View all available options:

```bash
python main.py --help
```

### List Available Options
See what datasets, tasks, and formats are available:

```bash
python main.py --list
```

## 📚 Command Reference

### Core Options

| Option | Short | Description | Default | Example |
|--------|-------|-------------|---------|---------|
| `--dataset` | `-d` | Single dataset to test | `healthcare-dataset` | `--dataset isbar` |
| `--datasets` | `-ds` | Multiple datasets | - | `--datasets healthcare-dataset isbar` |
| `--task` | `-t` | Single task to run | `answer_lookup` | `--task respondent_count` |
| `--tasks` | `-ts` | Multiple tasks | - | `--tasks answer_lookup respondent_count` |
| `--model` | `-m` | Single model to test | `all` | `--model openai` |
| `--models` | `-ms` | Multiple models | `all` | `--models openai deepseek` |
| `--formats` | `-f` | Data formats to test | `json xml` | `--formats json xml html` |
| `--cases` | `-c` | Cases per format | `5` | `--cases 10` |
| `--output` | `-o` | Output directory name (inside benchmark_results/) | Auto-generated | `--output my_results` |

### Control Options

| Option | Description | Default |
|--------|-------------|---------|
| `--excel` | Generate Excel report | `True` |
| `--no-excel` | Skip Excel generation | - |
| `--verbose` | Detailed logging | `False` |
| `--quiet` | Minimal output | `False` |
| `--list` | Show available options | - |

### Special Values

- Use `all` for datasets/tasks to run everything:
  ```bash
  python main.py --datasets all --tasks all
  ```

- Available formats: `json`, `xml`, `html`, `md`, `txt`, `ttl`
- Available models: 
  - `openai` → **gpt-3.5-turbo** (ChatGPT 3.5 Turbo)
  - `google` → **gemini-1.5-flash** (Google Gemini 1.5 Flash)
  - `deepseek` → **deepseek-chat** (DeepSeek Chat)

## 💡 Examples

### 1. Quick Test - Single Dataset
```bash
python main.py --dataset healthcare-dataset --cases 3
```
*Tests healthcare dataset with 3 cases per format (JSON, XML)*

### 2. Multiple Datasets and Tasks
```bash
python main.py --datasets healthcare-dataset isbar --tasks answer_lookup respondent_count --cases 5
```
*Comprehensive test across multiple datasets and tasks*

### 3. Format Comparison Study
```bash
python main.py --formats json xml html md --cases 10 --output format_study
```
*Compare 4 different data formats with more test cases (saves to benchmark_results/format_study/)*

### 4. Full Benchmark Suite
```bash
python main.py --datasets all --tasks all --cases 20 --output full_benchmark
```
*Run complete benchmark on all available data (saves to benchmark_results/full_benchmark/)*

### 5. Quick JSON-only Test
```bash
python main.py --formats json --cases 2 --no-excel --quiet
```
*Fast test with minimal output*

### 6. Research Study Setup
```bash
python main.py --datasets healthcare-dataset isbar --tasks answer_lookup answer_reverse_lookup conceptual_aggregation --formats json xml --cases 25 --output research_study_2025
```
*Comprehensive research-grade benchmark (saves to benchmark_results/research_study_2025/)*

### 7. Individual Model Testing
```bash
# Test only ChatGPT 3.5 Turbo (gpt-3.5-turbo)
python main.py --model openai --datasets all --tasks all --formats all --cases 2 --output chatgpt_only

# Test only DeepSeek Chat (deepseek-chat)
python main.py --model deepseek --datasets all --tasks all --formats all --cases 2 --output deepseek_only

# Test only Google Gemini 1.5 Flash (gemini-1.5-flash)
python main.py --model google --datasets healthcare-dataset isbar --tasks answer_lookup --cases 2 --output gemini_test
```
*Run individual models for focused testing*

### 8. Model Comparison
```bash
# Compare specific models
python main.py --models openai deepseek --datasets healthcare-dataset --tasks answer_lookup --formats json xml --cases 10 --output model_comparison
```
*Direct comparison between selected models*

## 📊 Understanding Output

### Progress Tracking
The benchmark shows real-time progress with tqdm progress bars:
- **Combination progress**: Shows dataset/task combinations being processed
- **Model evaluation progress**: Shows individual LLM evaluations with model names  
- **Prompt processing**: Shows progress through individual prompts for each model

### Directory Structure
```
benchmark_results/
└── my_experiment_name/
    └── run_20250117_143022/
        ├── summary.json                    # Overall statistics
        ├── benchmark_results_table.xlsx    # Excel report
        ├── healthcare-dataset/
        │   ├── answer_lookup/
        │   │   └── gpt_3.5_turbo_results.json
        │   └── answer_reverse_lookup/
        │       └── gpt_3.5_turbo_results.json
        └── isbar/
            ├── answer_lookup/
            │   └── gpt_3.5_turbo_results.json
            └── conceptual_aggregation/
                └── gpt_3.5_turbo_results.json
```

### Result Files

#### Individual Model Results (`*_results.json`)
```json
[
  {
    "case_id": "case_1",
    "data_format": "json",
    "model_name": "gpt-3.5-turbo",
    "prompt": "Based on the data, what is...",
    "expected_answer": "42",
    "llm_response": "42",
    "is_correct": true,
    "score": 1.0,
    "response_time": 1.23,
    "success": true,
    "error": null
  }
]
```

#### Summary Statistics (`summary.json`)
```json
{
  "timestamp": "2025-01-17T14:30:22",
  "overall_stats": {
    "total_cases": 100,
    "total_correct": 87,
    "overall_accuracy": 0.87
  },
  "by_provider": {
    "gpt-3.5-turbo": {"accuracy": 0.92, "avg_time": 1.1},
    "deepseek-chat": {"accuracy": 0.85, "avg_time": 2.3}
  },
  "by_format": {
    "json": {"accuracy": 0.89},
    "xml": {"accuracy": 0.91}
  }
}
```

#### Excel Report (`benchmark_results_table.xlsx`)
Interactive table showing:
- **Rows**: Data formats (JSON, XML, HTML, etc.)
- **Columns**: Dataset/Task combinations
- **Cells**: Performance metrics (correct/total cases)
- **Multi-level headers**: Dataset → Task → Model

## 🔧 Advanced Usage

### 1. Batch Processing
Create a script for multiple benchmark runs:

```bash
#!/bin/bash
# Run different format comparisons

python main.py --formats json xml --cases 50 --output json_vs_xml_study
python main.py --formats html md txt --cases 50 --output text_formats_study
python main.py --formats ttl --cases 50 --output semantic_web_study
```

### 2. Research Pipeline
```bash
# Phase 1: Quick exploration
python main.py --datasets all --cases 5 --output phase1_exploration

# Phase 2: Focused study
python main.py --datasets healthcare-dataset isbar --tasks answer_lookup answer_reverse_lookup --cases 25 --output phase2_focused

# Phase 3: Deep dive
python main.py --dataset healthcare-dataset --task answer_lookup --formats json xml html md txt ttl --cases 100 --output phase3_deep_dive
```

### 3. Performance Testing
```bash
# Test response times
python main.py --cases 1 --verbose --output performance_test

# Large-scale accuracy test
python main.py --cases 100 --output accuracy_test
```

### 4. Format-Specific Studies
```bash
# Structured formats
python main.py --formats json xml --output structured_formats

# Text formats
python main.py --formats md txt html --output text_formats

# Semantic web
python main.py --formats ttl --output semantic_web
```

## 🚨 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: No valid API keys found
```
**Solution**: Check your `.env` file has at least one valid API key.

#### 2. Dataset Not Found
```
Error: Dataset 'xyz' not found
```
**Solution**: Use `python main.py --list` to see available datasets.

#### 3. No Results Generated
```
Warning: No successful evaluations
```
**Solution**: Check API keys, internet connection, and model availability.

#### 4. Permission Errors
```
Error: Permission denied writing to directory
```
**Solution**: Ensure write permissions for output directory or change `--output`.

### Debug Mode
For detailed troubleshooting:

```bash
python main.py --verbose --cases 1 --output debug_run
```

### Verification Run
Test your setup:

```bash
python main.py --dataset healthcare-dataset --task answer_lookup --cases 1 --formats json --output verification
```

## 🎯 Best Practices

### 1. Start Small
```bash
# Begin with minimal test
python main.py --cases 1 --formats json
```

### 2. Incremental Scaling
```bash
# Gradually increase scope
python main.py --cases 5 --formats json xml
python main.py --cases 10 --formats json xml html
python main.py --datasets all --cases 20
```

### 3. Organized Output
```bash
# Use descriptive output directories (creates benchmark_results/experiment_2025_01_17_format_comparison/)
python main.py --output "experiment_2025_01_17_format_comparison"
```

### 4. Documentation
Keep notes on your experiments:
```bash
# Create experiment log
echo "Testing JSON vs XML performance" > experiment_log.txt
python main.py --formats json xml --cases 50 --output json_xml_comparison
echo "Results saved to json_xml_comparison/" >> experiment_log.txt
```

## 📈 Tips for Effective Benchmarking

1. **Start with defaults** to understand the system
2. **Use --list** to explore available options
3. **Begin with small case counts** (1-5) for quick iteration
4. **Scale up gradually** for comprehensive studies
5. **Use descriptive output directories** for organization
6. **Save Excel reports** for easy analysis and sharing
7. **Document your experiments** for reproducibility

---

## 🎉 You're Ready!

You now have everything you need to run effective LLM benchmarks with Q-Benchmark. Start with the [Quick Start](#quick-start) section and explore the [Examples](#examples) to find workflows that match your research needs.

Happy benchmarking! 🚀 