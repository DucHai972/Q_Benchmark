python benchmark_pipeline.py --model openai --openai-model gpt-4.1-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 2


python benchmark_pipeline.py --model google --google-model gemini-1.5-pro --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1

### Use here

cd ~/Q_Benchmark && source ~/Q_Benchmark/.venv/bin/activate

python3 benchmark_pipeline.py --model openai --openai-model gpt-4.1-mini --dataset healthcare-dataset --task answer_lookup --max-cases 3 --start-case 2