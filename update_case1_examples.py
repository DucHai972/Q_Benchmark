#!/usr/bin/env python3
import json
import os

def load_json_file(file_path):
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """Save JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_case1_examples_single_file(file_path):
    """Update CASE_1 examples in a single advanced prompts file."""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False, 0
    
    try:
        # Load the advanced prompts file
        advanced_prompts = load_json_file(file_path)
        
        # Find case_1 to get the question and answer
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
        
        # Build the new CASE_1 example string
        new_case_1_example = f"{case_1_question}\n\nDATA:\n\n[Insert the full data block here]\n\nAnswer: {case_1_answer}"
        
        print(f"✅ New CASE_1 example:")
        print(f"   Question: {case_1_question}")
        print(f"   Answer: {case_1_answer}")
        
        # Update all cases to use the new CASE_1 example
        updated_count = 0
        for i, prompt in enumerate(advanced_prompts):
            old_case_1 = prompt.get('CASE_1', '')
            advanced_prompts[i]['CASE_1'] = new_case_1_example
            updated_count += 1
        
        # Create backup
        backup_file = file_path + ".backup"
        if not os.path.exists(backup_file):
            print(f"💾 Creating backup: {backup_file}")
            save_json_file(backup_file, load_json_file(file_path))
        else:
            print(f"💾 Backup already exists: {backup_file}")
        
        # Save updated file
        save_json_file(file_path, advanced_prompts)
        
        return True, updated_count
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0

def update_healthcare_answer_lookup_test():
    """Test updating CASE_1 examples in healthcare answer_lookup file."""
    
    file_path = "/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_lookup_qa_pairs.json"
    
    print("🧪 Testing CASE_1 example update on healthcare answer_lookup...")
    print(f"📁 File: {file_path}")
    
    success, updated_count = update_case1_examples_single_file(file_path)
    
    if success:
        print(f"✅ Successfully updated {updated_count} cases")
        return True
    else:
        print("❌ Failed to update")
        return False

if __name__ == "__main__":
    success = update_healthcare_answer_lookup_test()
    
    if success:
        print("\n🎉 Test successful! CASE_1 examples updated.")
    else:
        print("\n❌ Test failed. Please check the logs above.")