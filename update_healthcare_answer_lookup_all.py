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

def update_all_healthcare_answer_lookup():
    """Update all 50 cases in healthcare answer_lookup with Q&A data."""
    
    # File paths
    qa_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.json"
    advanced_file = "/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_lookup_qa_pairs.json"
    
    # Check if files exist
    if not os.path.exists(qa_file):
        print(f"❌ Q&A file not found: {qa_file}")
        return False
    
    if not os.path.exists(advanced_file):
        print(f"❌ Advanced prompts file not found: {advanced_file}")
        return False
    
    # Load data
    print("📖 Loading Q&A data...")
    try:
        generated_qa = load_json_file(qa_file)
        print(f"   Found {len(generated_qa)} Q&A cases")
    except Exception as e:
        print(f"❌ Error loading Q&A file: {e}")
        return False
    
    print("📖 Loading advanced prompts...")
    try:
        advanced_prompts = load_json_file(advanced_file)
        print(f"   Found {len(advanced_prompts)} advanced prompt cases")
    except Exception as e:
        print(f"❌ Error loading advanced prompts: {e}")
        return False
    
    # Create backup (if not already exists from previous test)
    backup_file = advanced_file + ".backup"
    if not os.path.exists(backup_file):
        print(f"💾 Creating backup: {backup_file}")
        save_json_file(backup_file, load_json_file(advanced_file))
    else:
        print(f"💾 Backup already exists: {backup_file}")
    
    # Update cases
    updated_count = 0
    failed_cases = []
    
    print("\n🔄 Updating cases...")
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
            print(f"   ⚠️  {case_id}: Not found in advanced prompts")
            failed_cases.append(case_id)
            continue
        
        # Update the question and expected_answer
        old_question = prompt_case.get('question', 'N/A')
        old_answer = prompt_case.get('expected_answer', 'N/A')
        
        advanced_prompts[prompt_index]['question'] = qa['question']
        advanced_prompts[prompt_index]['expected_answer'] = qa['answer']
        updated_count += 1
        
        print(f"   ✅ {case_id}: Updated")
        print(f"      Question: {qa['question']}")
        print(f"      Answer: {qa['answer']}")
    
    if updated_count > 0:
        # Save updated file
        print(f"\n💾 Saving updated file...")
        save_json_file(advanced_file, advanced_prompts)
        print(f"✅ Successfully saved {advanced_file}")
    
    # Summary
    print(f"\n🎉 Summary:")
    print(f"   Total cases processed: {len(generated_qa)}")
    print(f"   Successfully updated: {updated_count}")
    print(f"   Failed cases: {len(failed_cases)}")
    
    if failed_cases:
        print(f"   Failed case IDs: {failed_cases}")
    
    return len(failed_cases) == 0

if __name__ == "__main__":
    print("🚀 Updating all 50 cases in healthcare answer_lookup...")
    success = update_all_healthcare_answer_lookup()
    
    if success:
        print("\n🎉 All cases updated successfully!")
    else:
        print("\n⚠️  Some cases failed to update. Check the logs above.")