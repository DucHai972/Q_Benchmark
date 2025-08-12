#!/bin/bash

# Reliable script to run 3 self_aug types on gpt-4.1-mini for all formats except JSON
# Usage: ./run_self_aug_gpt4mini_reliable.sh

set -e  # Exit on any error

echo "=========================================================="
echo "Running Self-Augmentation Benchmarks on GPT-4.1-mini"
echo "Formats: html, json, md, ttl, txt, xml (all formats)"
echo "Self-Aug Types: format_explaination, critical_values, structural_info"
echo "=========================================================="

# Define all formats including json
formats=("html" "json" "md" "ttl" "txt" "xml")

# Define the self-augmentation types
self_aug_types=("format_explaination" "critical_values" "structural_info")

# Total combinations: 6 formats × 3 self_aug types = 18
total_combinations=$((${#formats[@]} * ${#self_aug_types[@]}))
current_combination=0

echo "Total combinations to run: $total_combinations"
echo ""

# Run each combination
for self_aug in "${self_aug_types[@]}"; do
    for format in "${formats[@]}"; do
        current_combination=$((current_combination + 1))
        
        echo "[$current_combination/$total_combinations] Running: self_aug=$self_aug, format=$format"
        echo "----------------------------------------"
        
        # Run the benchmark (without --dataset all --task all to avoid potential issues)
        python benchmark_pipeline.py \
            --self_aug "$self_aug" \
            --model openai \
            --openai-model gpt-4.1-mini \
            --format "$format" \
            --max-cases 50
        
        if [ $? -eq 0 ]; then
            echo "✅ SUCCESS: self_aug=$self_aug, format=$format"
        else
            echo "❌ FAILED: self_aug=$self_aug, format=$format"
        fi
        echo ""
        
        # Add a small delay to avoid rate limiting
        sleep 2
    done
done

echo "=========================================================="
echo "✅ ALL SELF-AUGMENTATION BENCHMARKS COMPLETED!"
echo "=========================================================="
echo "Results saved in:"
echo "- benchmark_results/gpt-4.1-mini_format_explaination/"
echo "- benchmark_results/gpt-4.1-mini_critical_values/"
echo "- benchmark_results/gpt-4.1-mini_structural_info/"
echo "=========================================================="