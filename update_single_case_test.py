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

def update_single_case():
    """Test updating a single case in healthcare answer_lookup."""
    
    # File paths
    qa_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.json"
    advanced_file = "/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_lookup_qa_pairs.json"
    
    # Load data
    print("📖 Loading Q&A data...")
    generated_qa = load_json_file(qa_file)
    print(f"   Found {len(generated_qa)} Q&A cases")
    
    print("📖 Loading advanced prompts...")
    advanced_prompts = load_json_file(advanced_file)
    print(f"   Found {len(advanced_prompts)} advanced prompt cases")
    
    # Find case_2 to test with (skip case_1 since it might already be correct)
    test_case_id = "case_2"
    
    # Find the Q&A for test case
    qa_case = None
    for qa in generated_qa:
        if qa['case_id'] == test_case_id:
            qa_case = qa
            break
    
    if not qa_case:
        print(f"❌ {test_case_id} not found in Q&A data")
        return False
    
    print(f"✅ Found Q&A for {test_case_id}:")
    print(f"   Question: {qa_case['question']}")
    print(f"   Answer: {qa_case['answer']}")
    
    # Find the advanced prompt for test case
    prompt_case = None
    prompt_index = None
    for i, prompt in enumerate(advanced_prompts):
        if prompt['case_id'] == test_case_id:
            prompt_case = prompt
            prompt_index = i
            break
    
    if not prompt_case:
        print(f"❌ {test_case_id} not found in advanced prompts")
        return False
    
    print(f"✅ Found advanced prompt for {test_case_id}")
    print(f"   Current question: {prompt_case.get('question', 'N/A')}")
    print(f"   Current answer: {prompt_case.get('expected_answer', 'N/A')}")
    
    # Create backup
    backup_file = advanced_file + ".backup"
    print(f"💾 Creating backup: {backup_file}")
    save_json_file(backup_file, advanced_prompts)
    
    # Update the case
    print(f"🔄 Updating {test_case_id}...")
    advanced_prompts[prompt_index]['question'] = qa_case['question']
    advanced_prompts[prompt_index]['expected_answer'] = qa_case['answer']
    
    # Save updated file
    save_json_file(advanced_file, advanced_prompts)
    
    print(f"✅ Successfully updated {test_case_id}!")
    print(f"   New question: {qa_case['question']}")
    print(f"   New answer: {qa_case['answer']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing single case update...")
    success = update_single_case()
    
    if success:
        print("\n🎉 Test successful! Ready to proceed with all cases.")
    else:
        print("\n❌ Test failed. Please check the logs above.")