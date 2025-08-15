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

def standardize_advanced_prompts_file(file_path):
    """Standardize all cases in an advanced prompts file to use CASE_1 question and answer."""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False, 0
    
    try:
        # Load the advanced prompts file
        advanced_prompts = load_json_file(file_path)
        
        # Find case_1
        case_1_data = None
        for prompt in advanced_prompts:
            if prompt['case_id'] == 'case_1':
                case_1_data = prompt
                break
        
        if not case_1_data:
            print(f"❌ case_1 not found in {file_path}")
            return False, 0
        
        # Get the question and answer from case_1
        case_1_question = case_1_data.get('question', '')
        case_1_answer = case_1_data.get('expected_answer', '')
        
        if not case_1_question or case_1_answer is None:
            print(f"❌ case_1 missing question or answer in {file_path}")
            return False, 0
        
        # Update all cases to use case_1's question and answer
        updated_count = 0
        for i, prompt in enumerate(advanced_prompts):
            if prompt['case_id'] != 'case_1':  # Don't update case_1 itself
                advanced_prompts[i]['question'] = case_1_question
                advanced_prompts[i]['expected_answer'] = case_1_answer
                updated_count += 1
        
        # Create backup
        backup_file = file_path + ".backup"
        try:
            save_json_file(backup_file, load_json_file(file_path))
        except:
            pass  # Backup creation is optional
        
        # Save updated file
        save_json_file(file_path, advanced_prompts)
        
        return True, updated_count
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0

def main():
    """Standardize all advanced prompts files to use CASE_1 question and answer."""
    
    base_dir = "/insight-fast/dnguyen/Q_Benchmark"
    advanced_prompts_dir = os.path.join(base_dir, "advanced_prompts")
    
    # Get all datasets
    datasets = []
    for item in os.listdir(advanced_prompts_dir):
        item_path = os.path.join(advanced_prompts_dir, item)
        if os.path.isdir(item_path):
            datasets.append(item)
    
    print(f"Found datasets: {datasets}")
    
    total_files_processed = 0
    total_cases_updated = 0
    
    for dataset in datasets:
        print(f"\n🔄 Processing dataset: {dataset}")
        
        dataset_dir = os.path.join(advanced_prompts_dir, dataset)
        
        # Find all JSON files in this dataset directory
        json_files = []
        for file in os.listdir(dataset_dir):
            if file.endswith('.json') and not file.endswith('.backup'):
                json_files.append(file)
        
        print(f"  Found files: {json_files}")
        
        for json_file in json_files:
            file_path = os.path.join(dataset_dir, json_file)
            
            print(f"  📝 Standardizing {json_file}...")
            
            success, updated_count = standardize_advanced_prompts_file(file_path)
            
            if success:
                total_files_processed += 1
                total_cases_updated += updated_count
                print(f"    ✅ Standardized {updated_count} cases to use case_1 question and answer")
            else:
                print(f"    ❌ Failed to standardize")
    
    print(f"\n🎉 Summary:")
    print(f"  Total files processed: {total_files_processed}")
    print(f"  Total cases standardized: {total_cases_updated}")
    print(f"  All advanced prompts now use case_1 question and answer for consistency!")

if __name__ == "__main__":
    main()