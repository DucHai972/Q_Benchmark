"""
Simple Gemini Model Tester
A simple script to test custom prompts with the Gemini model
"""

import os
from dotenv import load_dotenv
from llm_clients import create_llm_client

def test_gemini_prompt(str_prompt: str):
    """
    Test a custom prompt with Gemini model
    
    Args:
        str_prompt: The prompt string to send to Gemini
    """
    # Load environment variables
    load_dotenv()
    
    # Get Google API key from environment
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        print("Error: GOOGLE_API_KEY not found in .env file")
        print("Please add your Google API key to the .env file:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return
    
    try:
        # Create Gemini client
        print("Initializing Gemini client...")
        client = create_llm_client("google", google_key, "gemini-1.5-flash")
        
        # Send prompt to Gemini
        print(f"\nSending prompt to Gemini...")
        print(f"Prompt: {str_prompt}")
        print("-" * 50)
        
        result = client.generate(str_prompt)
        
        # Display results
        if result['success']:
            print("✅ Success!")
            print(f"Response: {result['response']}")
            print(f"Response time: {result['response_time']:.2f} seconds")
            print(f"Model: {result['model']}")
        else:
            print("❌ Error occurred:")
            print(f"Error: {result['error']}")
            print(f"Response time: {result['response_time']:.2f} seconds")
            
    except Exception as e:
        print(f"❌ Failed to initialize or use Gemini: {e}")

if __name__ == "__main__":
    # Define your custom prompt here
    
    DATA = """
Medical conditions: A=Arthritis, B=Asthma, C=Cancer, D=Diabetes, E=Hypertension, F=Obesity

Patient 1: Medical_Condition "b"
Patient 2: Medical_Condition "e" 
Patient 3: Medical_Condition "b"
Patient 4: Medical_Condition "f"
Patient 5: Medical_Condition "a"
Patient 6: Medical_Condition "c"
"""
    str_prompt = f"Count how many patients have code D (Diabetes) or code F (Obesity).\n\n{DATA}\n\nAnswer with just the number."
    
    # Test the prompt
    test_gemini_prompt(str_prompt) 