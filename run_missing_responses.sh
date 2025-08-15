#!/bin/bash
# Auto-generated script to run missing benchmark responses for gpt-5-mini
# Total commands: 333

set -e  # Exit on any error

echo "Running command 1/255: healthcare-dataset > answer_lookup > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 41 && \

echo "Running command 2/255: healthcare-dataset > answer_lookup > json > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 41 && \

echo "Running command 3/255: healthcare-dataset > answer_lookup > json > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 49 && \

echo "Running command 4/255: healthcare-dataset > answer_reverse_lookup > html > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format html --max-cases 1 --start-case 31 && \

echo "Running command 5/255: healthcare-dataset > answer_reverse_lookup > html > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format html --max-cases 1 --start-case 40 && \

echo "Running command 6/255: healthcare-dataset > answer_reverse_lookup > json > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format json --max-cases 1 --start-case 31 && \

echo "Running command 7/255: healthcare-dataset > answer_reverse_lookup > json > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format json --max-cases 1 --start-case 40 && \

echo "Running command 8/255: healthcare-dataset > answer_reverse_lookup > md > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format md --max-cases 1 --start-case 31 && \

echo "Running command 9/255: healthcare-dataset > answer_reverse_lookup > md > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format md --max-cases 1 --start-case 40 && \

echo "Running command 10/255: healthcare-dataset > answer_reverse_lookup > ttl > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 30 && \

echo "Running command 11/255: healthcare-dataset > answer_reverse_lookup > ttl > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 31 && \

echo "Running command 12/255: healthcare-dataset > answer_reverse_lookup > ttl > case_37"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 37 && \

echo "Running command 13/255: healthcare-dataset > answer_reverse_lookup > ttl > case_38"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 38 && \

echo "Running command 14/255: healthcare-dataset > answer_reverse_lookup > ttl > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 40 && \

echo "Running command 15/255: healthcare-dataset > answer_reverse_lookup > ttl > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 45 && \

echo "Running command 16/255: healthcare-dataset > answer_reverse_lookup > ttl > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 47 && \

echo "Running command 17/255: healthcare-dataset > answer_reverse_lookup > ttl > case_48"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 48 && \

echo "Running command 18/255: healthcare-dataset > answer_reverse_lookup > ttl > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 49 && \

echo "Running command 19/255: healthcare-dataset > answer_reverse_lookup > txt > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format txt --max-cases 1 --start-case 31 && \

echo "Running command 20/255: healthcare-dataset > answer_reverse_lookup > txt > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format txt --max-cases 1 --start-case 40 && \

echo "Running command 21/255: healthcare-dataset > answer_reverse_lookup > xml > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format xml --max-cases 1 --start-case 31 && \

echo "Running command 22/255: healthcare-dataset > answer_reverse_lookup > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format xml --max-cases 1 --start-case 41 && \

echo "Running command 23/255: healthcare-dataset > answer_reverse_lookup > xml > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format xml --max-cases 1 --start-case 45 && \

echo "Running command 24/255: healthcare-dataset > answer_reverse_lookup > xml > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_reverse_lookup --format xml --max-cases 1 --start-case 49 && \

echo "Running command 25/255: healthcare-dataset > conceptual_aggregation > html > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format html --max-cases 1 --start-case 32 && \

echo "Running command 26/255: healthcare-dataset > conceptual_aggregation > html > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format html --max-cases 1 --start-case 40 && \

echo "Running command 27/255: healthcare-dataset > conceptual_aggregation > html > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format html --max-cases 1 --start-case 49 && \

echo "Running command 28/255: healthcare-dataset > conceptual_aggregation > json > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format json --max-cases 1 --start-case 35 && \

echo "Running command 29/255: healthcare-dataset > conceptual_aggregation > json > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format json --max-cases 1 --start-case 36 && \

echo "Running command 30/255: healthcare-dataset > conceptual_aggregation > json > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format json --max-cases 1 --start-case 40 && \

echo "Running command 31/255: healthcare-dataset > conceptual_aggregation > json > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format json --max-cases 1 --start-case 49 && \

echo "Running command 32/255: healthcare-dataset > conceptual_aggregation > md > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format md --max-cases 1 --start-case 31 && \

echo "Running command 33/255: healthcare-dataset > conceptual_aggregation > md > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format md --max-cases 1 --start-case 32 && \

echo "Running command 34/255: healthcare-dataset > conceptual_aggregation > md > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format md --max-cases 1 --start-case 33 && \

echo "Running command 35/255: healthcare-dataset > conceptual_aggregation > md > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format md --max-cases 1 --start-case 36 && \

echo "Running command 36/255: healthcare-dataset > conceptual_aggregation > md > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format md --max-cases 1 --start-case 49 && \

echo "Running command 37/255: healthcare-dataset > conceptual_aggregation > ttl > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format ttl --max-cases 1 --start-case 31 && \

echo "Running command 38/255: healthcare-dataset > conceptual_aggregation > ttl > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format ttl --max-cases 1 --start-case 32 && \

echo "Running command 39/255: healthcare-dataset > conceptual_aggregation > ttl > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format ttl --max-cases 1 --start-case 36 && \

echo "Running command 40/255: healthcare-dataset > conceptual_aggregation > ttl > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format ttl --max-cases 1 --start-case 49 && \

echo "Running command 41/255: healthcare-dataset > conceptual_aggregation > txt > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format txt --max-cases 1 --start-case 35 && \

echo "Running command 42/255: healthcare-dataset > conceptual_aggregation > txt > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format txt --max-cases 1 --start-case 36 && \

echo "Running command 43/255: healthcare-dataset > conceptual_aggregation > txt > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format txt --max-cases 1 --start-case 40 && \

echo "Running command 44/255: healthcare-dataset > conceptual_aggregation > txt > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format txt --max-cases 1 --start-case 49 && \

echo "Running command 45/255: healthcare-dataset > conceptual_aggregation > xml > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format xml --max-cases 1 --start-case 32 && \

echo "Running command 46/255: healthcare-dataset > conceptual_aggregation > xml > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format xml --max-cases 1 --start-case 36 && \

echo "Running command 47/255: healthcare-dataset > conceptual_aggregation > xml > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format xml --max-cases 1 --start-case 40 && \

echo "Running command 48/255: healthcare-dataset > conceptual_aggregation > xml > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task conceptual_aggregation --format xml --max-cases 1 --start-case 49 && \

echo "Running command 49/255: healthcare-dataset > multi_hop_relational_inference > xml > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task multi_hop_relational_inference --format xml --max-cases 1 --start-case 47 && \

echo "Running command 50/255: healthcare-dataset > respondent_count > html > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format html --max-cases 1 --start-case 27 && \

echo "Running command 51/255: healthcare-dataset > respondent_count > html > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format html --max-cases 1 --start-case 33 && \

echo "Running command 52/255: healthcare-dataset > respondent_count > html > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format html --max-cases 1 --start-case 43 && \

echo "Running command 53/255: healthcare-dataset > respondent_count > json > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format json --max-cases 1 --start-case 33 && \

echo "Running command 54/255: healthcare-dataset > respondent_count > json > case_34"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format json --max-cases 1 --start-case 34 && \

echo "Running command 55/255: healthcare-dataset > respondent_count > json > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format json --max-cases 1 --start-case 43 && \

echo "Running command 56/255: healthcare-dataset > respondent_count > md > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format md --max-cases 1 --start-case 27 && \

echo "Running command 57/255: healthcare-dataset > respondent_count > md > case_29"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format md --max-cases 1 --start-case 29 && \

echo "Running command 58/255: healthcare-dataset > respondent_count > md > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format md --max-cases 1 --start-case 33 && \

echo "Running command 59/255: healthcare-dataset > respondent_count > md > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format md --max-cases 1 --start-case 43 && \

echo "Running command 60/255: healthcare-dataset > respondent_count > ttl > case_34"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format ttl --max-cases 1 --start-case 34 && \

echo "Running command 61/255: healthcare-dataset > respondent_count > ttl > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format ttl --max-cases 1 --start-case 43 && \

echo "Running command 62/255: healthcare-dataset > respondent_count > txt > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format txt --max-cases 1 --start-case 27 && \

echo "Running command 63/255: healthcare-dataset > respondent_count > txt > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format txt --max-cases 1 --start-case 33 && \

echo "Running command 64/255: healthcare-dataset > respondent_count > xml > case_29"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format xml --max-cases 1 --start-case 29 && \

echo "Running command 65/255: healthcare-dataset > respondent_count > xml > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format xml --max-cases 1 --start-case 33 && \

echo "Running command 66/255: healthcare-dataset > respondent_count > xml > case_34"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format xml --max-cases 1 --start-case 34 && \

echo "Running command 67/255: healthcare-dataset > respondent_count > xml > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task respondent_count --format xml --max-cases 1 --start-case 43 && \

echo "Running command 68/255: healthcare-dataset > rule_based_querying > html > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 26 && \

echo "Running command 69/255: healthcare-dataset > rule_based_querying > html > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 27 && \

echo "Running command 70/255: healthcare-dataset > rule_based_querying > html > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 30 && \

echo "Running command 71/255: healthcare-dataset > rule_based_querying > html > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 35 && \

echo "Running command 72/255: healthcare-dataset > rule_based_querying > html > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 40 && \

echo "Running command 73/255: healthcare-dataset > rule_based_querying > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 41 && \

echo "Running command 74/255: healthcare-dataset > rule_based_querying > html > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 42 && \

echo "Running command 75/255: healthcare-dataset > rule_based_querying > html > case_44"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 44 && \

echo "Running command 76/255: healthcare-dataset > rule_based_querying > html > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 45 && \

echo "Running command 77/255: healthcare-dataset > rule_based_querying > html > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 46 && \

echo "Running command 78/255: healthcare-dataset > rule_based_querying > html > case_48"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format html --max-cases 1 --start-case 48 && \

echo "Running command 79/255: healthcare-dataset > rule_based_querying > json > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 26 && \

echo "Running command 80/255: healthcare-dataset > rule_based_querying > json > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 27 && \

echo "Running command 81/255: healthcare-dataset > rule_based_querying > json > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 30 && \

echo "Running command 82/255: healthcare-dataset > rule_based_querying > json > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 40 && \

echo "Running command 83/255: healthcare-dataset > rule_based_querying > json > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 41 && \

echo "Running command 84/255: healthcare-dataset > rule_based_querying > json > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 42 && \

echo "Running command 85/255: healthcare-dataset > rule_based_querying > json > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 45 && \

echo "Running command 86/255: healthcare-dataset > rule_based_querying > json > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format json --max-cases 1 --start-case 46 && \

echo "Running command 87/255: healthcare-dataset > rule_based_querying > md > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 26 && \

echo "Running command 88/255: healthcare-dataset > rule_based_querying > md > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 27 && \

echo "Running command 89/255: healthcare-dataset > rule_based_querying > md > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 30 && \

echo "Running command 90/255: healthcare-dataset > rule_based_querying > md > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 40 && \

echo "Running command 91/255: healthcare-dataset > rule_based_querying > md > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 41 && \

echo "Running command 92/255: healthcare-dataset > rule_based_querying > md > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 42 && \

echo "Running command 93/255: healthcare-dataset > rule_based_querying > md > case_44"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 44 && \

echo "Running command 94/255: healthcare-dataset > rule_based_querying > md > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format md --max-cases 1 --start-case 46 && \

echo "Running command 95/255: healthcare-dataset > rule_based_querying > ttl > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 26 && \

echo "Running command 96/255: healthcare-dataset > rule_based_querying > ttl > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 27 && \

echo "Running command 97/255: healthcare-dataset > rule_based_querying > ttl > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 30 && \

echo "Running command 98/255: healthcare-dataset > rule_based_querying > ttl > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 35 && \

echo "Running command 99/255: healthcare-dataset > rule_based_querying > ttl > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 40 && \

echo "Running command 100/255: healthcare-dataset > rule_based_querying > ttl > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 41 && \

echo "Running command 101/255: healthcare-dataset > rule_based_querying > ttl > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 42 && \

echo "Running command 102/255: healthcare-dataset > rule_based_querying > ttl > case_44"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 44 && \

echo "Running command 103/255: healthcare-dataset > rule_based_querying > ttl > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 45 && \

echo "Running command 104/255: healthcare-dataset > rule_based_querying > ttl > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 46 && \

echo "Running command 105/255: healthcare-dataset > rule_based_querying > ttl > case_48"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 48 && \

echo "Running command 106/255: healthcare-dataset > rule_based_querying > ttl > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format ttl --max-cases 1 --start-case 49 && \

echo "Running command 107/255: healthcare-dataset > rule_based_querying > txt > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 26 && \

echo "Running command 108/255: healthcare-dataset > rule_based_querying > txt > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 27 && \

echo "Running command 109/255: healthcare-dataset > rule_based_querying > txt > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 30 && \

echo "Running command 110/255: healthcare-dataset > rule_based_querying > txt > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 40 && \

echo "Running command 111/255: healthcare-dataset > rule_based_querying > txt > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 41 && \

echo "Running command 112/255: healthcare-dataset > rule_based_querying > txt > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 42 && \

echo "Running command 113/255: healthcare-dataset > rule_based_querying > txt > case_44"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 44 && \

echo "Running command 114/255: healthcare-dataset > rule_based_querying > txt > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 45 && \

echo "Running command 115/255: healthcare-dataset > rule_based_querying > txt > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format txt --max-cases 1 --start-case 46 && \

echo "Running command 116/255: healthcare-dataset > rule_based_querying > xml > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 26 && \

echo "Running command 117/255: healthcare-dataset > rule_based_querying > xml > case_30"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 30 && \

echo "Running command 118/255: healthcare-dataset > rule_based_querying > xml > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 40 && \

echo "Running command 119/255: healthcare-dataset > rule_based_querying > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 41 && \

echo "Running command 120/255: healthcare-dataset > rule_based_querying > xml > case_42"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 42 && \

echo "Running command 121/255: healthcare-dataset > rule_based_querying > xml > case_46"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task rule_based_querying --format xml --max-cases 1 --start-case 46 && \

echo "Running command 122/255: isbar > answer_lookup > html > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format html --max-cases 1 --start-case 47 && \

echo "Running command 123/255: isbar > answer_lookup > html > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format html --max-cases 1 --start-case 49 && \

echo "Running command 124/255: isbar > answer_lookup > json > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format json --max-cases 1 --start-case 28 && \

echo "Running command 125/255: isbar > answer_lookup > json > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format json --max-cases 1 --start-case 36 && \

echo "Running command 126/255: isbar > answer_lookup > json > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format json --max-cases 1 --start-case 40 && \

echo "Running command 127/255: isbar > answer_lookup > json > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format json --max-cases 1 --start-case 47 && \

echo "Running command 128/255: isbar > answer_lookup > json > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format json --max-cases 1 --start-case 49 && \

echo "Running command 129/255: isbar > answer_lookup > md > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format md --max-cases 1 --start-case 31 && \

echo "Running command 130/255: isbar > answer_lookup > md > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format md --max-cases 1 --start-case 36 && \

echo "Running command 131/255: isbar > answer_lookup > md > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format md --max-cases 1 --start-case 40 && \

echo "Running command 132/255: isbar > answer_lookup > md > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format md --max-cases 1 --start-case 49 && \

echo "Running command 133/255: isbar > answer_lookup > ttl > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 31 && \

echo "Running command 134/255: isbar > answer_lookup > ttl > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 33 && \

echo "Running command 135/255: isbar > answer_lookup > ttl > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 36 && \

echo "Running command 136/255: isbar > answer_lookup > ttl > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 40 && \

echo "Running command 137/255: isbar > answer_lookup > ttl > case_45"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 45 && \

echo "Running command 138/255: isbar > answer_lookup > ttl > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 47 && \

echo "Running command 139/255: isbar > answer_lookup > ttl > case_50"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format ttl --max-cases 1 --start-case 50 && \

echo "Running command 140/255: isbar > answer_lookup > txt > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 31 && \

echo "Running command 141/255: isbar > answer_lookup > txt > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 36 && \

echo "Running command 142/255: isbar > answer_lookup > txt > case_37"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 37 && \

echo "Running command 143/255: isbar > answer_lookup > txt > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 40 && \

echo "Running command 144/255: isbar > answer_lookup > txt > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 47 && \

echo "Running command 145/255: isbar > answer_lookup > txt > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format txt --max-cases 1 --start-case 49 && \

echo "Running command 146/255: isbar > answer_lookup > xml > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format xml --max-cases 1 --start-case 28 && \

echo "Running command 147/255: isbar > answer_lookup > xml > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format xml --max-cases 1 --start-case 33 && \

echo "Running command 148/255: isbar > answer_lookup > xml > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format xml --max-cases 1 --start-case 36 && \

echo "Running command 149/255: isbar > answer_lookup > xml > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format xml --max-cases 1 --start-case 40 && \

echo "Running command 150/255: isbar > answer_lookup > xml > case_47"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_lookup --format xml --max-cases 1 --start-case 47 && \

echo "Running command 151/255: isbar > answer_reverse_lookup > html > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format html --max-cases 1 --start-case 36 && \

echo "Running command 152/255: isbar > answer_reverse_lookup > html > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format html --max-cases 1 --start-case 40 && \

echo "Running command 153/255: isbar > answer_reverse_lookup > html > case_43"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format html --max-cases 1 --start-case 43 && \

echo "Running command 154/255: isbar > answer_reverse_lookup > html > case_49"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format html --max-cases 1 --start-case 49 && \

echo "Running command 155/255: isbar > answer_reverse_lookup > md > case_29"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format md --max-cases 1 --start-case 29 && \

echo "Running command 156/255: isbar > answer_reverse_lookup > md > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format md --max-cases 1 --start-case 40 && \

echo "Running command 157/255: isbar > answer_reverse_lookup > ttl > case_29"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 29 && \

echo "Running command 158/255: isbar > answer_reverse_lookup > txt > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format txt --max-cases 1 --start-case 40 && \

echo "Running command 159/255: isbar > answer_reverse_lookup > xml > case_40"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task answer_reverse_lookup --format xml --max-cases 1 --start-case 40 && \

echo "Running command 160/255: isbar > conceptual_aggregation > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task conceptual_aggregation --format html --max-cases 1 --start-case 41 && \

echo "Running command 161/255: isbar > conceptual_aggregation > txt > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task conceptual_aggregation --format txt --max-cases 1 --start-case 41 && \

echo "Running command 162/255: isbar > multi_hop_relational_inference > html > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task multi_hop_relational_inference --format html --max-cases 1 --start-case 31 && \

echo "Running command 163/255: isbar > rule_based_querying > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task rule_based_querying --format html --max-cases 1 --start-case 41 && \

echo "Running command 164/255: isbar > rule_based_querying > ttl > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task rule_based_querying --format ttl --max-cases 1 --start-case 41 && \

echo "Running command 165/255: isbar > rule_based_querying > txt > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task rule_based_querying --format txt --max-cases 1 --start-case 41 && \

echo "Running command 166/255: isbar > rule_based_querying > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset isbar --task rule_based_querying --format xml --max-cases 1 --start-case 41 && \

echo "Running command 167/255: self-reported-mental-health > answer_lookup > html > case_14"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format html --max-cases 1 --start-case 14 && \

echo "Running command 168/255: self-reported-mental-health > answer_lookup > html > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format html --max-cases 1 --start-case 35 && \

echo "Running command 169/255: self-reported-mental-health > answer_lookup > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format html --max-cases 1 --start-case 41 && \

echo "Running command 170/255: self-reported-mental-health > answer_lookup > json > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format json --max-cases 1 --start-case 41 && \

echo "Running command 171/255: self-reported-mental-health > answer_lookup > md > case_4"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format md --max-cases 1 --start-case 4 && \

echo "Running command 172/255: self-reported-mental-health > answer_lookup > md > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format md --max-cases 1 --start-case 17 && \

echo "Running command 173/255: self-reported-mental-health > answer_lookup > md > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format md --max-cases 1 --start-case 28 && \

echo "Running command 174/255: self-reported-mental-health > answer_lookup > md > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format md --max-cases 1 --start-case 35 && \

echo "Running command 175/255: self-reported-mental-health > answer_lookup > ttl > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format ttl --max-cases 1 --start-case 28 && \

echo "Running command 176/255: self-reported-mental-health > answer_lookup > ttl > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format ttl --max-cases 1 --start-case 41 && \

echo "Running command 177/255: self-reported-mental-health > answer_lookup > txt > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format txt --max-cases 1 --start-case 16 && \

echo "Running command 178/255: self-reported-mental-health > answer_lookup > txt > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format txt --max-cases 1 --start-case 17 && \

echo "Running command 179/255: self-reported-mental-health > answer_lookup > txt > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format txt --max-cases 1 --start-case 41 && \

echo "Running command 180/255: self-reported-mental-health > answer_lookup > xml > case_14"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 14 && \

echo "Running command 181/255: self-reported-mental-health > answer_lookup > xml > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 17 && \

echo "Running command 182/255: self-reported-mental-health > answer_lookup > xml > case_27"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 27 && \

echo "Running command 183/255: self-reported-mental-health > answer_lookup > xml > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 28 && \

echo "Running command 184/255: self-reported-mental-health > answer_lookup > xml > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 31 && \

echo "Running command 185/255: self-reported-mental-health > answer_lookup > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_lookup --format xml --max-cases 1 --start-case 41 && \

echo "Running command 186/255: self-reported-mental-health > answer_reverse_lookup > html > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format html --max-cases 1 --start-case 10 && \

echo "Running command 187/255: self-reported-mental-health > answer_reverse_lookup > json > case_3"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format json --max-cases 1 --start-case 3 && \

echo "Running command 188/255: self-reported-mental-health > answer_reverse_lookup > json > case_13"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format json --max-cases 1 --start-case 13 && \

echo "Running command 189/255: self-reported-mental-health > answer_reverse_lookup > json > case_24"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format json --max-cases 1 --start-case 24 && \

echo "Running command 190/255: self-reported-mental-health > answer_reverse_lookup > md > case_22"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format md --max-cases 1 --start-case 22 && \

echo "Running command 191/255: self-reported-mental-health > answer_reverse_lookup > ttl > case_3"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 3 && \

echo "Running command 192/255: self-reported-mental-health > answer_reverse_lookup > ttl > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 10 && \

echo "Running command 193/255: self-reported-mental-health > answer_reverse_lookup > ttl > case_22"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 22 && \

echo "Running command 194/255: self-reported-mental-health > answer_reverse_lookup > txt > case_2"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format txt --max-cases 1 --start-case 2 && \

echo "Running command 195/255: self-reported-mental-health > answer_reverse_lookup > txt > case_3"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format txt --max-cases 1 --start-case 3 && \

echo "Running command 196/255: self-reported-mental-health > answer_reverse_lookup > txt > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format txt --max-cases 1 --start-case 10 && \

echo "Running command 197/255: self-reported-mental-health > answer_reverse_lookup > txt > case_22"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format txt --max-cases 1 --start-case 22 && \

echo "Running command 198/255: self-reported-mental-health > answer_reverse_lookup > xml > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format xml --max-cases 1 --start-case 10 && \

echo "Running command 199/255: self-reported-mental-health > answer_reverse_lookup > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task answer_reverse_lookup --format xml --max-cases 1 --start-case 41 && \

echo "Running command 200/255: self-reported-mental-health > multi_hop_relational_inference > ttl > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task multi_hop_relational_inference --format ttl --max-cases 1 --start-case 32 && \

echo "Running command 201/255: self-reported-mental-health > multi_hop_relational_inference > ttl > case_37"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task multi_hop_relational_inference --format ttl --max-cases 1 --start-case 37 && \

echo "Running command 202/255: self-reported-mental-health > multi_hop_relational_inference > xml > case_29"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task multi_hop_relational_inference --format xml --max-cases 1 --start-case 29 && \

echo "Running command 203/255: self-reported-mental-health > multi_hop_relational_inference > xml > case_32"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task multi_hop_relational_inference --format xml --max-cases 1 --start-case 32 && \

echo "Running command 204/255: self-reported-mental-health > respondent_count > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task respondent_count --format xml --max-cases 1 --start-case 41 && \

echo "Running command 205/255: self-reported-mental-health > rule_based_querying > html > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format html --max-cases 1 --start-case 28 && \

echo "Running command 206/255: self-reported-mental-health > rule_based_querying > html > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format html --max-cases 1 --start-case 33 && \

echo "Running command 207/255: self-reported-mental-health > rule_based_querying > html > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format html --max-cases 1 --start-case 41 && \

echo "Running command 208/255: self-reported-mental-health > rule_based_querying > json > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format json --max-cases 1 --start-case 28 && \

echo "Running command 209/255: self-reported-mental-health > rule_based_querying > json > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format json --max-cases 1 --start-case 33 && \

echo "Running command 210/255: self-reported-mental-health > rule_based_querying > json > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format json --max-cases 1 --start-case 41 && \

echo "Running command 211/255: self-reported-mental-health > rule_based_querying > md > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format md --max-cases 1 --start-case 33 && \

echo "Running command 212/255: self-reported-mental-health > rule_based_querying > md > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format md --max-cases 1 --start-case 41 && \

echo "Running command 213/255: self-reported-mental-health > rule_based_querying > ttl > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format ttl --max-cases 1 --start-case 28 && \

echo "Running command 214/255: self-reported-mental-health > rule_based_querying > ttl > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format ttl --max-cases 1 --start-case 33 && \

echo "Running command 215/255: self-reported-mental-health > rule_based_querying > ttl > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format ttl --max-cases 1 --start-case 36 && \

echo "Running command 216/255: self-reported-mental-health > rule_based_querying > ttl > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format ttl --max-cases 1 --start-case 41 && \

echo "Running command 217/255: self-reported-mental-health > rule_based_querying > txt > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format txt --max-cases 1 --start-case 28 && \

echo "Running command 218/255: self-reported-mental-health > rule_based_querying > txt > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format txt --max-cases 1 --start-case 33 && \

echo "Running command 219/255: self-reported-mental-health > rule_based_querying > txt > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format txt --max-cases 1 --start-case 41 && \

echo "Running command 220/255: self-reported-mental-health > rule_based_querying > xml > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format xml --max-cases 1 --start-case 28 && \

echo "Running command 221/255: self-reported-mental-health > rule_based_querying > xml > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format xml --max-cases 1 --start-case 33 && \

echo "Running command 222/255: self-reported-mental-health > rule_based_querying > xml > case_41"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset self-reported-mental-health --task rule_based_querying --format xml --max-cases 1 --start-case 41 && \

echo "Running command 223/255: stack-overflow-2022 > answer_lookup > html > case_2"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format html --max-cases 1 --start-case 2 && \

echo "Running command 224/255: stack-overflow-2022 > answer_lookup > html > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format html --max-cases 1 --start-case 5 && \

echo "Running command 225/255: stack-overflow-2022 > answer_lookup > html > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format html --max-cases 1 --start-case 16 && \

echo "Running command 226/255: stack-overflow-2022 > answer_lookup > html > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format html --max-cases 1 --start-case 17 && \

echo "Running command 227/255: stack-overflow-2022 > answer_lookup > html > case_24"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format html --max-cases 1 --start-case 24 && \

echo "Running command 228/255: stack-overflow-2022 > answer_lookup > json > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format json --max-cases 1 --start-case 5 && \

echo "Running command 229/255: stack-overflow-2022 > answer_lookup > json > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format json --max-cases 1 --start-case 16 && \

echo "Running command 230/255: stack-overflow-2022 > answer_lookup > md > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format md --max-cases 1 --start-case 5 && \

echo "Running command 231/255: stack-overflow-2022 > answer_lookup > md > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format md --max-cases 1 --start-case 10 && \

echo "Running command 232/255: stack-overflow-2022 > answer_lookup > md > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format md --max-cases 1 --start-case 16 && \

echo "Running command 233/255: stack-overflow-2022 > answer_lookup > ttl > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format ttl --max-cases 1 --start-case 5 && \

echo "Running command 234/255: stack-overflow-2022 > answer_lookup > ttl > case_6"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format ttl --max-cases 1 --start-case 6 && \

echo "Running command 235/255: stack-overflow-2022 > answer_lookup > ttl > case_10"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format ttl --max-cases 1 --start-case 10 && \

echo "Running command 236/255: stack-overflow-2022 > answer_lookup > ttl > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format ttl --max-cases 1 --start-case 17 && \

echo "Running command 237/255: stack-overflow-2022 > answer_lookup > ttl > case_33"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format ttl --max-cases 1 --start-case 33 && \

echo "Running command 238/255: stack-overflow-2022 > answer_lookup > txt > case_2"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format txt --max-cases 1 --start-case 2 && \

echo "Running command 239/255: stack-overflow-2022 > answer_lookup > txt > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format txt --max-cases 1 --start-case 5 && \

echo "Running command 240/255: stack-overflow-2022 > answer_lookup > txt > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format txt --max-cases 1 --start-case 16 && \

echo "Running command 241/255: stack-overflow-2022 > answer_lookup > txt > case_23"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format txt --max-cases 1 --start-case 23 && \

echo "Running command 242/255: stack-overflow-2022 > answer_lookup > xml > case_5"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format xml --max-cases 1 --start-case 5 && \

echo "Running command 243/255: stack-overflow-2022 > answer_lookup > xml > case_16"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format xml --max-cases 1 --start-case 16 && \

echo "Running command 244/255: stack-overflow-2022 > answer_lookup > xml > case_17"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_lookup --format xml --max-cases 1 --start-case 17 && \

echo "Running command 245/255: stack-overflow-2022 > answer_reverse_lookup > html > case_35"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format html --max-cases 1 --start-case 35 && \

echo "Running command 246/255: stack-overflow-2022 > answer_reverse_lookup > html > case_37"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format html --max-cases 1 --start-case 37 && \

echo "Running command 247/255: stack-overflow-2022 > answer_reverse_lookup > json > case_28"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format json --max-cases 1 --start-case 28 && \

echo "Running command 248/255: stack-overflow-2022 > answer_reverse_lookup > md > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format md --max-cases 1 --start-case 36 && \

echo "Running command 249/255: stack-overflow-2022 > answer_reverse_lookup > ttl > case_31"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 31 && \

echo "Running command 250/255: stack-overflow-2022 > answer_reverse_lookup > ttl > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 36 && \

echo "Running command 251/255: stack-overflow-2022 > answer_reverse_lookup > ttl > case_37"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format ttl --max-cases 1 --start-case 37 && \

echo "Running command 252/255: stack-overflow-2022 > answer_reverse_lookup > xml > case_26"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format xml --max-cases 1 --start-case 26 && \

echo "Running command 253/255: stack-overflow-2022 > answer_reverse_lookup > xml > case_36"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task answer_reverse_lookup --format xml --max-cases 1 --start-case 36 && \

echo "Running command 254/255: stack-overflow-2022 > conceptual_aggregation > ttl > case_34"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset stack-overflow-2022 --task conceptual_aggregation --format ttl --max-cases 1 --start-case 34 && \

echo "Running command 255/255: sus-uta7 > multi_hop_relational_inference > ttl > case_11"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset sus-uta7 --task multi_hop_relational_inference --format ttl --max-cases 1 --start-case 11 && \

echo "Running command 256/333: healthcare-dataset > answer_lookup > html > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 2 && \

echo "Running command 257/333: healthcare-dataset > answer_lookup > json > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 2 && \

echo "Running command 258/333: healthcare-dataset > answer_lookup > md > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 2 && \

echo "Running command 259/333: healthcare-dataset > answer_lookup > ttl > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 2 && \

echo "Running command 260/333: healthcare-dataset > answer_lookup > txt > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 2 && \

echo "Running command 261/333: healthcare-dataset > answer_lookup > xml > case_2 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 2 && \

echo "Running command 262/333: healthcare-dataset > answer_lookup > html > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 3 && \

echo "Running command 263/333: healthcare-dataset > answer_lookup > json > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 3 && \

echo "Running command 264/333: healthcare-dataset > answer_lookup > md > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 3 && \

echo "Running command 265/333: healthcare-dataset > answer_lookup > ttl > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 3 && \

echo "Running command 266/333: healthcare-dataset > answer_lookup > txt > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 3 && \

echo "Running command 267/333: healthcare-dataset > answer_lookup > xml > case_3 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 3 && \

echo "Running command 268/333: healthcare-dataset > answer_lookup > html > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 4 && \

echo "Running command 269/333: healthcare-dataset > answer_lookup > json > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 4 && \

echo "Running command 270/333: healthcare-dataset > answer_lookup > md > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 4 && \

echo "Running command 271/333: healthcare-dataset > answer_lookup > ttl > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 4 && \

echo "Running command 272/333: healthcare-dataset > answer_lookup > txt > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 4 && \

echo "Running command 273/333: healthcare-dataset > answer_lookup > xml > case_4 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 4 && \

echo "Running command 274/333: healthcare-dataset > answer_lookup > html > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 11 && \

echo "Running command 275/333: healthcare-dataset > answer_lookup > json > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 11 && \

echo "Running command 276/333: healthcare-dataset > answer_lookup > md > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 11 && \

echo "Running command 277/333: healthcare-dataset > answer_lookup > ttl > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 11 && \

echo "Running command 278/333: healthcare-dataset > answer_lookup > txt > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 11 && \

echo "Running command 279/333: healthcare-dataset > answer_lookup > xml > case_11 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 11 && \

echo "Running command 280/333: healthcare-dataset > answer_lookup > html > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 15 && \

echo "Running command 281/333: healthcare-dataset > answer_lookup > json > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 15 && \

echo "Running command 282/333: healthcare-dataset > answer_lookup > md > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 15 && \

echo "Running command 283/333: healthcare-dataset > answer_lookup > ttl > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 15 && \

echo "Running command 284/333: healthcare-dataset > answer_lookup > txt > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 15 && \

echo "Running command 285/333: healthcare-dataset > answer_lookup > xml > case_15 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 15 && \

echo "Running command 286/333: healthcare-dataset > answer_lookup > html > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 16 && \

echo "Running command 287/333: healthcare-dataset > answer_lookup > json > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 16 && \

echo "Running command 288/333: healthcare-dataset > answer_lookup > md > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 16 && \

echo "Running command 289/333: healthcare-dataset > answer_lookup > ttl > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 16 && \

echo "Running command 290/333: healthcare-dataset > answer_lookup > txt > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 16 && \

echo "Running command 291/333: healthcare-dataset > answer_lookup > xml > case_16 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 16 && \

echo "Running command 292/333: healthcare-dataset > answer_lookup > html > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 18 && \

echo "Running command 293/333: healthcare-dataset > answer_lookup > json > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 18 && \

echo "Running command 294/333: healthcare-dataset > answer_lookup > md > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 18 && \

echo "Running command 295/333: healthcare-dataset > answer_lookup > ttl > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 18 && \

echo "Running command 296/333: healthcare-dataset > answer_lookup > txt > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 18 && \

echo "Running command 297/333: healthcare-dataset > answer_lookup > xml > case_18 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 18 && \

echo "Running command 298/333: healthcare-dataset > answer_lookup > html > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 19 && \

echo "Running command 299/333: healthcare-dataset > answer_lookup > json > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 19 && \

echo "Running command 300/333: healthcare-dataset > answer_lookup > md > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 19 && \

echo "Running command 301/333: healthcare-dataset > answer_lookup > ttl > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 19 && \

echo "Running command 302/333: healthcare-dataset > answer_lookup > txt > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 19 && \

echo "Running command 303/333: healthcare-dataset > answer_lookup > xml > case_19 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 19 && \

echo "Running command 304/333: healthcare-dataset > answer_lookup > html > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 21 && \

echo "Running command 305/333: healthcare-dataset > answer_lookup > json > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 21 && \

echo "Running command 306/333: healthcare-dataset > answer_lookup > md > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 21 && \

echo "Running command 307/333: healthcare-dataset > answer_lookup > ttl > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 21 && \

echo "Running command 308/333: healthcare-dataset > answer_lookup > txt > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 21 && \

echo "Running command 309/333: healthcare-dataset > answer_lookup > xml > case_21 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 21 && \

echo "Running command 310/333: healthcare-dataset > answer_lookup > html > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 22 && \

echo "Running command 311/333: healthcare-dataset > answer_lookup > json > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 22 && \

echo "Running command 312/333: healthcare-dataset > answer_lookup > md > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 22 && \

echo "Running command 313/333: healthcare-dataset > answer_lookup > ttl > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 22 && \

echo "Running command 314/333: healthcare-dataset > answer_lookup > txt > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 22 && \

echo "Running command 315/333: healthcare-dataset > answer_lookup > xml > case_22 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 22 && \

echo "Running command 316/333: healthcare-dataset > answer_lookup > html > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 25 && \

echo "Running command 317/333: healthcare-dataset > answer_lookup > json > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 25 && \

echo "Running command 318/333: healthcare-dataset > answer_lookup > md > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 25 && \

echo "Running command 319/333: healthcare-dataset > answer_lookup > ttl > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 25 && \

echo "Running command 320/333: healthcare-dataset > answer_lookup > txt > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 25 && \

echo "Running command 321/333: healthcare-dataset > answer_lookup > xml > case_25 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 25 && \

echo "Running command 322/333: healthcare-dataset > answer_lookup > html > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 33 && \

echo "Running command 323/333: healthcare-dataset > answer_lookup > json > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 33 && \

echo "Running command 324/333: healthcare-dataset > answer_lookup > md > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 33 && \

echo "Running command 325/333: healthcare-dataset > answer_lookup > ttl > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 33 && \

echo "Running command 326/333: healthcare-dataset > answer_lookup > txt > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 33 && \

echo "Running command 327/333: healthcare-dataset > answer_lookup > xml > case_33 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 33 && \

echo "Running command 328/333: healthcare-dataset > answer_lookup > html > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format html --max-cases 1 --start-case 47 && \

echo "Running command 329/333: healthcare-dataset > answer_lookup > json > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format json --max-cases 1 --start-case 47 && \

echo "Running command 330/333: healthcare-dataset > answer_lookup > md > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format md --max-cases 1 --start-case 47 && \

echo "Running command 331/333: healthcare-dataset > answer_lookup > ttl > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format ttl --max-cases 1 --start-case 47 && \

echo "Running command 332/333: healthcare-dataset > answer_lookup > txt > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format txt --max-cases 1 --start-case 47 && \

echo "Running command 333/333: healthcare-dataset > answer_lookup > xml > case_47 (RERUN)"
python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset healthcare-dataset --task answer_lookup --format xml --max-cases 1 --start-case 47
