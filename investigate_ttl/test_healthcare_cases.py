"""
Test Healthcare Cases with Gemini
Tests cases from extracted_ttl_failures/healthcare-dataset
using TTL data from modified_inextracted_ttl directory and compares with expected answers
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from llm_clients import create_llm_client
from evaluator import BenchmarkEvaluator
import time

def load_ttl_data(case_id, source_task):
    """Load TTL data from the modified_inextracted_ttl directory."""
    ttl_file = Path(f"modified_inextracted_ttl/{case_id}_{source_task}.ttl")
    if ttl_file.exists():
        with open(ttl_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise FileNotFoundError(f"TTL file not found: {ttl_file}")

def test_case_with_gemini(client, case_data):
    """Test a single case with Gemini and return results."""
    case_id = case_data['case_id']
    source_task = case_data['source_task']
    expected_answer = case_data['expected_answer']
    str_prompt_template = case_data['str_prompt']
    
    print(f"\nTesting {case_id} ({source_task})...")
    
    try:
        # Load TTL data
        ttl_data = load_ttl_data(case_id, source_task)
        
        # Create the actual prompt by replacing {DATA} placeholder
        str_prompt = str_prompt_template.replace("{DATA}", ttl_data)
        
        # Send to Gemini
        print(f"Sending prompt to Gemini...")
        result = client.generate(str_prompt)
        
        # Get response
        if result['success']:
            llm_response = result['response']
            response_time = result['response_time']
            print(f"✅ Success! Response time: {response_time:.2f}s")
        else:
            llm_response = f"ERROR: {result['error']}"
            response_time = result['response_time']
            print(f"❌ Error: {result['error']}")
        
        # Use the evaluator for proper evaluation
        evaluator = BenchmarkEvaluator()
        evaluation = evaluator.evaluate_response(llm_response, expected_answer, source_task)
        
        # Determine if correct based on score threshold
        is_correct = evaluation['score'] >= 0.8
        
        return {
            'case_id': case_id,
            'source_task': source_task,
            'str_prompt': str_prompt,
            'llm_response': llm_response,
            'expected_answer': expected_answer,
            'is_correct': is_correct,
            'response_time': response_time,
            'evaluation': evaluation
        }
        
    except Exception as e:
        print(f"❌ Error processing case: {e}")
        return {
            'case_id': case_id,
            'source_task': source_task,
            'str_prompt': str_prompt_template,
            'llm_response': f"ERROR: {str(e)}",
            'expected_answer': expected_answer,
            'is_correct': False,
            'response_time': 0
        }

def main():
    """Main function to test the first 3 cases."""
    # Load environment variables
    load_dotenv()
    
    # Get Google API key
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        print("Error: GOOGLE_API_KEY not found in .env file")
        return
    
    try:
        # Initialize Gemini client
        print("Initializing Gemini client...")
        client = create_llm_client("google", google_key, "gemini-1.5-flash")
        
        # Get the first 3 JSON files from extracted_ttl_failures/healthcare-dataset
        input_dir = Path("extracted_ttl_failures/healthcare-dataset")
        json_files = sorted([f for f in input_dir.glob("*.json") if f.name != "all_healthcare_cases.json"])[:]
        
        print(f"Testing {len(json_files)} cases: {[f.name for f in json_files]}")
        
        results = []
        
        # Test each case
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            result = test_case_with_gemini(client, case_data)
            results.append(result)
            
            # Add delay to avoid rate limits
            time.sleep(1)
        
        # Write results to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"healthcare_test_results_{timestamp}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("HEALTHCARE CASES TEST RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Cases: {len(results)}\n")
            f.write("=" * 50 + "\n\n")
            
            correct_count = 0
            
            for i, result in enumerate(results, 1):
                f.write(f"CASE {i}: {result['case_id']} ({result['source_task']})\n")
                f.write("-" * 40 + "\n")
                f.write(f"Expected Answer: {result['expected_answer']}\n")
                f.write(f"LLM Response: {result['llm_response']}\n")
                f.write(f"Correct: {'✅ YES' if result['is_correct'] else '❌ NO'}\n")
                f.write(f"Response Time: {result['response_time']:.2f}s\n")
                
                # Add evaluation details
                if 'evaluation' in result:
                    eval_data = result['evaluation']
                    f.write(f"Evaluation Score: {eval_data['score']:.3f}\n")
                    f.write(f"Exact Match: {'✅' if eval_data['exact_match'] else '❌'}\n")
                    f.write(f"Normalized Match: {'✅' if eval_data['normalized_match'] else '❌'}\n")
                    f.write(f"Partial Match: {'✅' if eval_data['partial_match'] else '❌'}\n")
                    if eval_data['error']:
                        f.write(f"Evaluation Error: {eval_data['error']}\n")
                
                f.write("\n")
                
                # Add the full prompt and data
                f.write("PROMPT:\n")
                f.write("-" * 20 + "\n")
                f.write(result['str_prompt'])
                f.write("\n\n")
                
                if result['is_correct']:
                    correct_count += 1
            
            f.write("=" * 50 + "\n")
            f.write(f"SUMMARY: {correct_count}/{len(results)} cases correct\n")
            f.write(f"Accuracy: {(correct_count/len(results)*100):.1f}%\n")
        
        print(f"\nResults saved to: {output_file}")
        print(f"Summary: {correct_count}/{len(results)} cases correct ({(correct_count/len(results)*100):.1f}%)")
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")

if __name__ == "__main__":
    main() 