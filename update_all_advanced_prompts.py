#!/usr/bin/env python3
import json
import os
from pathlib import Path

def load_json_file(file_path):
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """Save JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_advanced_prompts(qa_file, advanced_prompts_file):
    """Update advanced prompts with Q&A data."""
    # Check if files exist
    if not os.path.exists(qa_file):
        print(f"❌ Q&A file not found: {qa_file}")
        return False, 0, []
    
    if not os.path.exists(advanced_prompts_file):
        print(f"❌ Advanced prompts file not found: {advanced_prompts_file}")
        return False, 0, []
    
    # Load data
    try:
        generated_qa = load_json_file(qa_file)
        advanced_prompts = load_json_file(advanced_prompts_file)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False, 0, []
    
    # Update cases
    updated_count = 0
    failed_cases = []
    
    for qa in generated_qa:
        case_id = qa['case_id']
        
        # Find the case in advanced prompts
        prompt_case = None
        prompt_index = None
        for i, prompt in enumerate(advanced_prompts):
            if prompt['case_id'] == case_id:
                prompt_case = prompt
                prompt_index = i
                break
        
        if not prompt_case:
            failed_cases.append(case_id)
            continue
        
        # Update the question and expected_answer
        advanced_prompts[prompt_index]['question'] = qa['question']
        advanced_prompts[prompt_index]['expected_answer'] = qa['answer']
        updated_count += 1
    
    if updated_count > 0:
        # Create backup
        backup_file = advanced_prompts_file + ".backup"
        try:
            save_json_file(backup_file, load_json_file(advanced_prompts_file))
        except:
            pass  # Backup creation is optional
        
        # Save updated file
        save_json_file(advanced_prompts_file, advanced_prompts)
    
    return True, updated_count, failed_cases

def get_task_mapping():
    """Get mapping between Q&A filenames and advanced prompt filenames."""
    return {
        'answer_lookup': 'answer_lookup_qa_pairs',
        'answer_reverse_lookup': 'answer_reverse_lookup_qa_pairs', 
        'conceptual_aggregation': 'conceptual_aggregation_qa_pairs',
        'multi_hop_relational_inference': 'multi_hop_relational_inference_qa_pairs',
        'multi_hop_relational': 'multi_hop_relational_inference_qa_pairs',  # Handle both naming patterns
        'respondent_count': 'respondent_count_qa_pairs',
        'rule_based_querying': 'rule_based_querying_qa_pairs',
        'rule_based': 'rule_based_querying_qa_pairs'  # Handle both naming patterns
    }

def main():
    """Update all advanced prompts with generated Q&A data."""
    
    base_dir = "/insight-fast/dnguyen/Q_Benchmark"
    questions_design_dir = os.path.join(base_dir, "questions_design")
    advanced_prompts_dir = os.path.join(base_dir, "advanced_prompts")
    
    # Get all datasets
    datasets = []
    for item in os.listdir(questions_design_dir):
        item_path = os.path.join(questions_design_dir, item)
        if os.path.isdir(item_path):
            datasets.append(item)
    
    print(f"Found datasets: {datasets}")
    
    task_mapping = get_task_mapping()
    
    total_updated = 0
    total_files = 0
    
    for dataset in datasets:
        print(f"\n🔄 Processing dataset: {dataset}")
        
        dataset_qa_dir = os.path.join(questions_design_dir, dataset)
        dataset_advanced_dir = os.path.join(advanced_prompts_dir, dataset)
        
        if not os.path.exists(dataset_advanced_dir):
            print(f"⚠️  Advanced prompts directory not found: {dataset_advanced_dir}")
            continue
        
        # Find all Q&A files in this dataset
        qa_files = []
        for file in os.listdir(dataset_qa_dir):
            if file.endswith('_qa.json'):
                qa_files.append(file)
        
        print(f"  Found Q&A files: {qa_files}")
        
        for qa_file in qa_files:
            # Extract task name from filename
            # e.g., "healthcare_answer_lookup_qa.json" -> "answer_lookup"
            task = None
            for task_key in task_mapping.keys():
                if task_key in qa_file:
                    task = task_key
                    break
            
            if not task:
                print(f"  ⚠️  Could not determine task for file: {qa_file}")
                continue
            
            # Build paths
            qa_file_path = os.path.join(dataset_qa_dir, qa_file)
            advanced_file = f"{dataset}_{task_mapping[task]}.json"
            advanced_file_path = os.path.join(dataset_advanced_dir, advanced_file)
            
            print(f"  📝 Updating {task}...")
            print(f"    Q&A: {qa_file_path}")
            print(f"    Advanced: {advanced_file_path}")
            
            # Update the files
            success, updated_count, failed_cases = update_advanced_prompts(qa_file_path, advanced_file_path)
            
            if success:
                total_files += 1
                total_updated += updated_count
                print(f"    ✅ Updated {updated_count} cases")
                if failed_cases:
                    print(f"    ⚠️  Failed cases: {failed_cases}")
            else:
                print(f"    ❌ Failed to update")
    
    print(f"\n🎉 Summary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Total cases updated: {total_updated}")
    print(f"  All advanced prompts have been updated with generated Q&A data!")

if __name__ == "__main__":
    main()