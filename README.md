# LLM Data Format Benchmark Pipeline

A simple pipeline to evaluate LLM performance across different data formats (JSON, XML, HTML, Markdown, TXT, TTL).

## Setup

1. Install dependencies:
```bash
pip install python-dotenv openai google-generativeai
```

2. Create `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

## Usage

Run the benchmark:

```python
from benchmark_pipeline import BenchmarkPipeline

# Initialize pipeline
pipeline = BenchmarkPipeline()

# Run benchmark (customize as needed)
results_dir = pipeline.run_benchmark(
    dataset="healthcare-dataset",  # or None for all datasets
    task="answer_lookup",          # or None for all tasks
    max_cases=5,                   # limit for testing
    formats=["json", "xml", "md"]  # or None for all formats
)

print(f"Results saved to: {results_dir}")
```

## Output

The pipeline creates a timestamped results folder with:

- `prompts.json` - All generated prompts
- `{provider}_results.json` - Results for each LLM provider
- `analysis.json` - Performance analysis
- `summary_report.txt` - Human-readable summary

## Analysis

The pipeline evaluates:
- **Success Rate**: How often the LLM responded successfully
- **Exact Match Rate**: How often the response exactly matched expected answer
- **Normalized Match Rate**: Case-insensitive matches
- **Average Score**: Weighted scoring (exact=1.0, normalized=0.9, partial=0.5)
- **Response Time**: Average time per response

Results are analyzed by:
- Data format (JSON vs XML vs Markdown, etc.)
- Task type (lookup vs aggregation vs reasoning)
- LLM provider (OpenAI vs Google vs DeepSeek)

The pipeline identifies the best-performing data format overall and for each provider. 