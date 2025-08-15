#!/usr/bin/env python3
import json
import os

def load_generated_qa(qa_file_path):
    """Load the generated Q&A pairs from questions_design."""
    with open(qa_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_advanced_prompts(advanced_prompts_path):
    """Load the advanced prompts template."""
    with open(advanced_prompts_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_single_case(advanced_prompts, generated_qa, case_id):
    """Update a single case in advanced prompts with generated Q&A data."""
    # Find the case in generated Q&A
    qa_case = None
    for qa in generated_qa:
        if qa['case_id'] == case_id:
            qa_case = qa
            break
    
    if not qa_case:
        print(f"Case {case_id} not found in generated Q&A")
        return False
    
    # Find the case in advanced prompts
    prompt_case = None
    prompt_index = None
    for i, prompt in enumerate(advanced_prompts):
        if prompt['case_id'] == case_id:
            prompt_case = prompt
            prompt_index = i
            break
    
    if not prompt_case:
        print(f"Case {case_id} not found in advanced prompts")
        return False
    
    # Update the question and expected_answer
    old_question = prompt_case['question']
    old_answer = prompt_case['expected_answer']
    
    advanced_prompts[prompt_index]['question'] = qa_case['question']
    advanced_prompts[prompt_index]['expected_answer'] = qa_case['answer']
    
    print(f"Updated {case_id}:")
    print(f"  Old question: {old_question}")
    print(f"  New question: {qa_case['question']}")
    print(f"  Old answer: {old_answer}")
    print(f"  New answer: {qa_case['answer']}")
    
    return True

def update_all_cases(advanced_prompts, generated_qa):
    """Update all cases in advanced prompts with generated Q&A data."""
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
            print(f"⚠️  Case {case_id} not found in advanced prompts")
            failed_cases.append(case_id)
            continue
        
        # Update the question and expected_answer
        advanced_prompts[prompt_index]['question'] = qa['question']
        advanced_prompts[prompt_index]['expected_answer'] = qa['answer']
        updated_count += 1
        
        print(f"✅ Updated {case_id}")
    
    return updated_count, failed_cases

def main():
    """Update all 50 cases of healthcare answer_lookup."""
    
    # Paths
    qa_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/healthcare-dataset/healthcare_answer_lookup_qa.json"
    advanced_prompts_file = "/insight-fast/dnguyen/Q_Benchmark/advanced_prompts/healthcare-dataset/healthcare-dataset_answer_lookup_qa_pairs.json"
    
    # Load data
    print("Loading generated Q&A data...")
    generated_qa = load_generated_qa(qa_file)
    print(f"Loaded {len(generated_qa)} Q&A pairs")
    
    print("Loading advanced prompts...")
    advanced_prompts = load_advanced_prompts(advanced_prompts_file)
    print(f"Loaded {len(advanced_prompts)} advanced prompt entries")
    
    # Update all cases
    print("\nUpdating all cases...")
    updated_count, failed_cases = update_all_cases(advanced_prompts, generated_qa)
    
    if updated_count > 0:
        # Save the updated file
        backup_file = advanced_prompts_file + ".backup_all"
        print(f"\nCreating backup at {backup_file}")
        
        # Create backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            original_data = load_advanced_prompts(advanced_prompts_file)
            json.dump(original_data, f, indent=2, ensure_ascii=False)
        
        # Save updated file
        print(f"Saving updated file to {advanced_prompts_file}")
        with open(advanced_prompts_file, 'w', encoding='utf-8') as f:
            json.dump(advanced_prompts, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully updated {updated_count} cases!")
        
        if failed_cases:
            print(f"⚠️  Failed to update {len(failed_cases)} cases: {failed_cases}")
        else:
            print("🎉 All cases updated successfully!")
    else:
        print("❌ No cases were updated")

if __name__ == "__main__":
    main()