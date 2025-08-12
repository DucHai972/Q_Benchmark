#!/bin/bash

# Script to run Gemini-2.5-Flash on normal config and all self_aug configs
# Usage: ./run_gemini_all_configs.sh

set -e  # Exit on any error

echo "=========================================================="
echo "Running Gemini-2.5-Flash Benchmarks"
echo "Configs: NORMAL + 3 Self-Aug Types"
echo "Formats: html, json, md, ttl, txt, xml (all formats)"
echo "=========================================================="

# Define all formats including json
formats=("html" "json" "md" "ttl" "txt" "xml")

# Define the configurations: normal + 3 self-aug types
configs=("normal" "format_explaination" "critical_values" "structural_info")

# Total combinations: 6 formats × 4 configs = 24
total_combinations=$((${#formats[@]} * ${#configs[@]}))
current_combination=0

echo "Total combinations to run: $total_combinations"
echo ""

# Run each combination
for config in "${configs[@]}"; do
    for format in "${formats[@]}"; do
        current_combination=$((current_combination + 1))
        
        echo "[$current_combination/$total_combinations] Running: config=$config, format=$format"
        echo "----------------------------------------"
        
        # Build command based on config type
        if [ "$config" = "normal" ]; then
            # Run normal benchmark
            python benchmark_pipeline.py \
                --model google \
                --google-model gemini-2.5-flash \
                --format "$format" \
                --max-cases 50
        else
            # Run self-augmentation benchmark
            python benchmark_pipeline.py \
                --self_aug "$config" \
                --model google \
                --google-model gemini-2.5-flash \
                --format "$format" \
                --max-cases 50
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ SUCCESS: config=$config, format=$format"
        else
            echo "❌ FAILED: config=$config, format=$format"
        fi
        echo ""
        
        # Add a small delay to avoid rate limiting
        sleep 2
    done
done

echo "=========================================================="
echo "✅ ALL GEMINI BENCHMARKS COMPLETED!"
echo "=========================================================="
echo "Results saved in:"
echo "- benchmark_results/gemini-2.5-flash/ (normal config)"
echo "- benchmark_results/gemini-2.5-flash_format_explaination/"
echo "- benchmark_results/gemini-2.5-flash_critical_values/"
echo "- benchmark_results/gemini-2.5-flash_structural_info/"
echo "=========================================================="