#!/usr/bin/env python3
"""
Script to generate Python benchmark commands for missing responses.
"""

def parse_missing_responses():
    """Parse the missing responses data and generate commands."""
    
    # Missing responses data from the check script output
    missing_data = [
        # healthcare-dataset
        ("healthcare-dataset", "answer_lookup", "html", ["case_41"]),
        ("healthcare-dataset", "answer_lookup", "json", ["case_41", "case_49"]),
        ("healthcare-dataset", "answer_reverse_lookup", "html", ["case_31", "case_40"]),
        ("healthcare-dataset", "answer_reverse_lookup", "json", ["case_31", "case_40"]),
        ("healthcare-dataset", "answer_reverse_lookup", "md", ["case_31", "case_40"]),
        ("healthcare-dataset", "answer_reverse_lookup", "ttl", ["case_30", "case_31", "case_37", "case_38", "case_40", "case_45", "case_47", "case_48", "case_49"]),
        ("healthcare-dataset", "answer_reverse_lookup", "txt", ["case_31", "case_40"]),
        ("healthcare-dataset", "answer_reverse_lookup", "xml", ["case_31", "case_41", "case_45", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "html", ["case_32", "case_40", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "json", ["case_35", "case_36", "case_40", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "md", ["case_31", "case_32", "case_33", "case_36", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "ttl", ["case_31", "case_32", "case_36", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "txt", ["case_35", "case_36", "case_40", "case_49"]),
        ("healthcare-dataset", "conceptual_aggregation", "xml", ["case_32", "case_36", "case_40", "case_49"]),
        ("healthcare-dataset", "multi_hop_relational_inference", "xml", ["case_47"]),
        ("healthcare-dataset", "respondent_count", "html", ["case_27", "case_33", "case_43"]),
        ("healthcare-dataset", "respondent_count", "json", ["case_33", "case_34", "case_43"]),
        ("healthcare-dataset", "respondent_count", "md", ["case_27", "case_29", "case_33", "case_43"]),
        ("healthcare-dataset", "respondent_count", "ttl", ["case_34", "case_43"]),
        ("healthcare-dataset", "respondent_count", "txt", ["case_27", "case_33"]),
        ("healthcare-dataset", "respondent_count", "xml", ["case_29", "case_33", "case_34", "case_43"]),
        ("healthcare-dataset", "rule_based_querying", "html", ["case_26", "case_27", "case_30", "case_35", "case_40", "case_41", "case_42", "case_44", "case_45", "case_46", "case_48"]),
        ("healthcare-dataset", "rule_based_querying", "json", ["case_26", "case_27", "case_30", "case_40", "case_41", "case_42", "case_45", "case_46"]),
        ("healthcare-dataset", "rule_based_querying", "md", ["case_26", "case_27", "case_30", "case_40", "case_41", "case_42", "case_44", "case_46"]),
        ("healthcare-dataset", "rule_based_querying", "ttl", ["case_26", "case_27", "case_30", "case_35", "case_40", "case_41", "case_42", "case_44", "case_45", "case_46", "case_48", "case_49"]),
        ("healthcare-dataset", "rule_based_querying", "txt", ["case_26", "case_27", "case_30", "case_40", "case_41", "case_42", "case_44", "case_45", "case_46"]),
        ("healthcare-dataset", "rule_based_querying", "xml", ["case_26", "case_30", "case_40", "case_41", "case_42", "case_46"]),
        
        # isbar
        ("isbar", "answer_lookup", "html", ["case_47", "case_49"]),
        ("isbar", "answer_lookup", "json", ["case_28", "case_36", "case_40", "case_47", "case_49"]),
        ("isbar", "answer_lookup", "md", ["case_31", "case_36", "case_40", "case_49"]),
        ("isbar", "answer_lookup", "ttl", ["case_31", "case_33", "case_36", "case_40", "case_45", "case_47", "case_50"]),
        ("isbar", "answer_lookup", "txt", ["case_31", "case_36", "case_37", "case_40", "case_47", "case_49"]),
        ("isbar", "answer_lookup", "xml", ["case_28", "case_33", "case_36", "case_40", "case_47"]),
        ("isbar", "answer_reverse_lookup", "html", ["case_36", "case_40", "case_43", "case_49"]),
        ("isbar", "answer_reverse_lookup", "md", ["case_29", "case_40"]),
        ("isbar", "answer_reverse_lookup", "ttl", ["case_29"]),
        ("isbar", "answer_reverse_lookup", "txt", ["case_40"]),
        ("isbar", "answer_reverse_lookup", "xml", ["case_40"]),
        ("isbar", "conceptual_aggregation", "html", ["case_41"]),
        ("isbar", "conceptual_aggregation", "txt", ["case_41"]),
        ("isbar", "multi_hop_relational_inference", "html", ["case_31"]),
        ("isbar", "rule_based_querying", "html", ["case_41"]),
        ("isbar", "rule_based_querying", "ttl", ["case_41"]),
        ("isbar", "rule_based_querying", "txt", ["case_41"]),
        ("isbar", "rule_based_querying", "xml", ["case_41"]),
        
        # self-reported-mental-health
        ("self-reported-mental-health", "answer_lookup", "html", ["case_14", "case_35", "case_41"]),
        ("self-reported-mental-health", "answer_lookup", "json", ["case_41"]),
        ("self-reported-mental-health", "answer_lookup", "md", ["case_4", "case_17", "case_28", "case_35"]),
        ("self-reported-mental-health", "answer_lookup", "ttl", ["case_28", "case_41"]),
        ("self-reported-mental-health", "answer_lookup", "txt", ["case_16", "case_17", "case_41"]),
        ("self-reported-mental-health", "answer_lookup", "xml", ["case_14", "case_17", "case_27", "case_28", "case_31", "case_41"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "html", ["case_10"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "json", ["case_3", "case_13", "case_24"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "md", ["case_22"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "ttl", ["case_3", "case_10", "case_22"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "txt", ["case_2", "case_3", "case_10", "case_22"]),
        ("self-reported-mental-health", "answer_reverse_lookup", "xml", ["case_10", "case_41"]),
        ("self-reported-mental-health", "multi_hop_relational_inference", "ttl", ["case_32", "case_37"]),
        ("self-reported-mental-health", "multi_hop_relational_inference", "xml", ["case_29", "case_32"]),
        ("self-reported-mental-health", "respondent_count", "xml", ["case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "html", ["case_28", "case_33", "case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "json", ["case_28", "case_33", "case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "md", ["case_33", "case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "ttl", ["case_28", "case_33", "case_36", "case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "txt", ["case_28", "case_33", "case_41"]),
        ("self-reported-mental-health", "rule_based_querying", "xml", ["case_28", "case_33", "case_41"]),
        
        # stack-overflow-2022
        ("stack-overflow-2022", "answer_lookup", "html", ["case_2", "case_5", "case_16", "case_17", "case_24"]),
        ("stack-overflow-2022", "answer_lookup", "json", ["case_5", "case_16"]),
        ("stack-overflow-2022", "answer_lookup", "md", ["case_5", "case_10", "case_16"]),
        ("stack-overflow-2022", "answer_lookup", "ttl", ["case_5", "case_6", "case_10", "case_17", "case_33"]),
        ("stack-overflow-2022", "answer_lookup", "txt", ["case_2", "case_5", "case_16", "case_23"]),
        ("stack-overflow-2022", "answer_lookup", "xml", ["case_5", "case_16", "case_17"]),
        ("stack-overflow-2022", "answer_reverse_lookup", "html", ["case_35", "case_37"]),
        ("stack-overflow-2022", "answer_reverse_lookup", "json", ["case_28"]),
        ("stack-overflow-2022", "answer_reverse_lookup", "md", ["case_36"]),
        ("stack-overflow-2022", "answer_reverse_lookup", "ttl", ["case_31", "case_36", "case_37"]),
        ("stack-overflow-2022", "answer_reverse_lookup", "xml", ["case_26", "case_36"]),
        ("stack-overflow-2022", "conceptual_aggregation", "ttl", ["case_34"]),
        
        # sus-uta7
        ("sus-uta7", "multi_hop_relational_inference", "ttl", ["case_11"]),
    ]
    
    commands = []
    total_cases = 0
    
    for dataset, task, format_type, cases in missing_data:
        for case in cases:
            case_num = case.replace("case_", "")
            command = f"python3 benchmark_pipeline.py --model openai --openai-model gpt-5-mini --dataset {dataset} --task {task} --format {format_type} --max-cases 1 --start-case {case_num}"
            commands.append(command)
            total_cases += 1
    
    return commands, total_cases

if __name__ == "__main__":
    commands, total = parse_missing_responses()
    print(f"Generated {total} commands for missing responses")
    
    # Write to shell script
    with open("run_missing_responses.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Auto-generated script to run missing benchmark responses for gpt-5-mini\n")
        f.write(f"# Total commands: {total}\n\n")
        f.write("set -e  # Exit on any error\n\n")
        
        for i, cmd in enumerate(commands, 1):
            f.write(f"echo \"Running command {i}/{total}: {cmd.split('--dataset')[1].split('--task')[0].strip()} > {cmd.split('--task')[1].split('--format')[0].strip()} > {cmd.split('--format')[1].split('--max-cases')[0].strip()} > case_{cmd.split('--start-case')[1].strip()}\"\n")
            f.write(f"{cmd}")
            if i < total:
                f.write(" && \\")
            f.write("\n")
            if i < total:
                f.write("\n")
    
    print("Shell script saved as 'run_missing_responses.sh'")