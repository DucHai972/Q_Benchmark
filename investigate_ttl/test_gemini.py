"""
Simple Gemini Model Tester
A simple script to test custom prompts with the Gemini model
"""

import os
import sys

# Add parent directory to path to import modules from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
# Questions
:Name pred:text "What is your name? [Open-ended]" .
:Age pred:text "What is your age? [Open-ended]" .
:Gender pred:text "What is your gender? [MCQ: A. Female B. Male]" .
:Blood_Type pred:text "What is your blood type? [MCQ: A. A+ B. A- C. AB+ D. AB- E. B+ F. B- G. O+ H. O-]" .
:Medical_Condition pred:text "What is your medical condition? [MCQ: A. Arthritis B. Asthma C. Cancer D. Diabetes E. Hypertension F. Obesity]" .
:Date_of_Admission pred:text "What is your date of admission? [Open-ended]" .
:Doctor pred:text "What is your doctor? [Open-ended]" .
:Hospital pred:text "What is your hospital? [Open-ended]" .
:Insurance_Provider pred:text "What is your insurance provider? [MCQ: A. Aetna B. Blue Cross C. Cigna D. Medicare E. UnitedHealthcare]" .
:Billing_Amount pred:text "What is your billing amount? [Open-ended]" .
:Room_Number pred:text "What is your room number? [Open-ended]" .
:Admission_Type pred:text "What is your admission type? [MCQ: A. Elective B. Emergency C. Urgent]" .
:Discharge_Date pred:text "What is your discharge date? [Open-ended]" .
:Medication pred:text "What is your medication? [MCQ: A. Aspirin B. Ibuprofen C. Lipitor D. Paracetamol E. Penicillin]" .
:Test_Results pred:text "What is your test results? [MCQ: A. Abnormal B. Inconclusive C. Normal]" .

# =========
# Responses
:Respondent94 a :Person ;
    pred:Name "mIcHAeL MaRTIn" ;
    pred:Age "84" ;
    pred:Gender "b" ;
    pred:Blood_Type "a" ;
    pred:Medical_Condition "B" ;  
    pred:Date_of_Admission "2022-09-06" ;
    pred:Doctor "John Summers" ;
    pred:Hospital "Sons Horn and" ;
    pred:Insurance_Provider "c" ;
    pred:Billing_Amount "23685" ;
    pred:Room_Number "162" ;
    pred:Admission_Type "c" ;
    pred:Discharge_Date "2022-09-27" ;
    pred:Medication "b" ;
    pred:Test_Results "b" .

:Respondent47 a :Person ;
    pred:Name "chRIsTOpHEr CHaPmAN" ;
    pred:Age "31" ;
    pred:Gender "a" ;
    pred:Blood_Type "g" ;
    pred:Medical_Condition "E" ;  
    pred:Date_of_Admission "2021-12-01" ;
    pred:Doctor "Emily Patterson" ;
    pred:Hospital "Ltd Schwartz" ;
    pred:Insurance_Provider "c" ;
    pred:Billing_Amount "29615" ;
    pred:Room_Number "211" ;
    pred:Admission_Type "a" ;
    pred:Discharge_Date "2021-12-09" ;
    pred:Medication "d" ;
    pred:Test_Results "c" .

:Respondent149 a :Person ;
    pred:Name "RoBErt hIGGInS" ;
    pred:Age "42" ;
    pred:Gender "b" ;
    pred:Blood_Type "d" ;
    pred:Medical_Condition "B" ;
    pred:Date_of_Admission "2021-05-06" ;
    pred:Doctor "Scott Davis" ;
    pred:Hospital "and Ford Lee, Rodriguez" ;
    pred:Insurance_Provider "d" ;
    pred:Billing_Amount "13356" ;
    pred:Room_Number "451" ;
    pred:Admission_Type "a" ;
    pred:Discharge_Date "2021-05-29" ;
    pred:Medication "b" ;
    pred:Test_Results "b" .

:Respondent84 a :Person ;
    pred:Name "DIAnE brAnch" ;
    pred:Age "44" ;
    pred:Gender "b" ;
    pred:Blood_Type "g" ;
    pred:Medical_Condition "F" ; 
    pred:Date_of_Admission "2020-05-30" ;
    pred:Doctor "Juan Acevedo" ;
    pred:Hospital "Perez and Sons" ;
    pred:Insurance_Provider "c" ;
    pred:Billing_Amount "22841" ;
    pred:Room_Number "410" ;
    pred:Admission_Type "b" ;
    pred:Discharge_Date "2020-06-14" ;
    pred:Medication "a" ;
    pred:Test_Results "b" .

:Respondent112 a :Person ;
    pred:Name "MARK priCE" ;
    pred:Age "18" ;
    pred:Gender "b" ;
    pred:Blood_Type "f" ;
    pred:Medical_Condition "A" ;  
    pred:Date_of_Admission "2022-09-22" ;
    pred:Doctor "Krystal Fox" ;
    pred:Hospital "Hall Roberts and Duarte," ;
    pred:Insurance_Provider "d" ;
    pred:Billing_Amount "31486" ;
    pred:Room_Number "440" ;
    pred:Admission_Type "b" ;
    pred:Discharge_Date "2022-10-14" ;
    pred:Medication "b" ;
    pred:Test_Results "c" .

:Respondent15 a :Person ;
    pred:Name "bROOkE brady" ;
    pred:Age "44" ;
    pred:Gender "a" ;
    pred:Blood_Type "c" ;
    pred:Medical_Condition "C" ; 
    pred:Date_of_Admission "2021-10-08" ;
    pred:Doctor "Roberta Stewart" ;
    pred:Hospital "Morris-Arellano" ;
    pred:Insurance_Provider "e" ;
    pred:Billing_Amount "40702" ;
    pred:Room_Number "182" ;
    pred:Admission_Type "c" ;
    pred:Discharge_Date "2021-10-13" ;
    pred:Medication "d" ;
    pred:Test_Results "c" .
"""
    str_prompt = f"You are a meticulous data analyst AI. Your primary function is to accurately analyze structured data and provide precise, verifiable answers.\n\nYou will be given a dataset with two key parts:\n\nA 'questions' section: This is your data dictionary or schema. It is the single source of truth for understanding what each field and score means. Refer to it carefully.\n\nA 'responses' section: This contains the raw data from each individual respondent.\n\nTo answer the question correctly, you must first use the 'questions' schema to fully understand the context and meaning of the data points within the 'responses'. Do not rely on any prior knowledge outside of this provided data. Base your entire analysis on the information given.\n\nOUTPUT INSTRUCTIONS:\nProvide your final answer directly and concisely. Your output should contain only the answer itself, without explaining your thought process or methodology. For example:\n\nIf the question asks for a count, provide only the final number (e.g., \"42\").\n\nIf the question asks for a list of names or IDs, provide them as a simple comma-separated list (e.g., \"17, 21, 23\").\n\nIf the question asks for a specific text comment, provide only that text.\n\nQUESTION:\nHow many patients have metabolic conditions (Diabetes or Obesity) and who are they? Explain your answer.\n\nDATA: {DATA}"
    
    # Test the prompt
    test_gemini_prompt(str_prompt) 
   