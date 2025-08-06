#!/usr/bin/env python3
"""
Script to fix XML format in conceptual_aggregation to match answer_lookup format:
1. Restructure questions to use question_group with base_question and sub_questions
2. Keep response format (it's already correct)
"""

import os
import json

def generate_xml_from_json(json_data):
    """Generate properly formatted XML content from JSON data"""
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<questionnaire>
  <questions>
    <question id="Year of birth">What is your date of birth? [Open-ended]</question>
    <question id="Gender">What is your gender? [MCQ: 1. Male 2. Female]</question>
    <question id="Socio-economic status">What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]</question>
    <question id="Ethnic identity">According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]</question>
    <question_group id="Parental Education">
      <base_question>How many years of education did your parents receive? [Open-ended]</base_question>
      <sub_questions>
        <question id="Father">Father?</question>
        <question id="Mother">Mother?</question>
      </sub_questions>
    </question_group>
    <question id="Life satisfaction">In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]</question>
    <question id="Happiness">How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Laughter">How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Learning">Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Enjoyment">How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Worry">How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Depression">How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Anger">How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Stress">How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question id="Loneliness">How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]</question>
    <question_group id="Emotional Regulation Frequency">
      <base_question>Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]</base_question>
      <sub_questions>
        <question id="Upset by Unexpected Events">how often have you been upset because of something that happened unexpectedly?</question>
        <question id="Unable to Control Important Things">how often have you felt that you were unable to control the important things in your life?</question>
        <question id="Nervous and Stressed">how often have you felt nervous and stressed?</question>
        <question id="Lacked Confidence Handling Problems">how often have you felt confident about your ability to handle your personal problems?</question>
        <question id="Things Going Your Way">how often have you felt that things were going your way?</question>
        <question id="Unable to Cope">how often have you found that you could not cope with all the things that you had to do?</question>
        <question id="Irritated by Life">how often have you been able to control irritations in your life?</question>
        <question id="On Top of Things">how often have you felt that you were on top of things?</question>
        <question id="Angered by Uncontrollable Events">how often have you been angered because of things that happened that were outside of your control?</question>
        <question id="Felt Overwhelmed">how often have you felt difficulties were piling up so high that you could not overcome them?</question>
      </sub_questions>
    </question_group>
    <question_group id="Anxiety Symptoms Frequency">
      <base_question>Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]</base_question>
      <sub_questions>
        <question id="Feeling Nervous or On Edge">Feeling nervous, anxious, or on edge</question>
        <question id="Uncontrollable Worrying">Not being able to stop or control worrying</question>
        <question id="Excessive Worry">Worrying too much about different things</question>
        <question id="Trouble Relaxing">Trouble relaxing</question>
        <question id="Restlessness">Being so restless that it is hard to sit still</question>
        <question id="Irritability">Becoming easily annoyed or irritable</question>
        <question id="Fear Something Awful Might Happen">Feeling afraid, as if something awful might happen</question>
      </sub_questions>
    </question_group>
    <question_group id="Depressive Symptoms Frequency">
      <base_question>Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems?</base_question>
      <sub_questions>
        <question id="Anhedonia">Little interest or pleasure in doing things</question>
        <question id="Depressed Mood">Feeling down, depressed, or hopeless</question>
        <question id="Sleep Problems">Trouble falling or staying asleep, or sleeping too much</question>
        <question id="Fatigue">Feeling tired or having little energy</question>
        <question id="Appetite Changes">Poor appetite or overeating</question>
        <question id="Feelings of Worthlessness">Feeling bad about yourself or that you are a failure or have let yourself or your family down</question>
        <question id="Concentration Difficulties">Trouble concentrating on things, such as reading the newspaper or watching television</question>
        <question id="Psychomotor Changes">Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual</question>
        <question id="Suicidal Thoughts">Thoughts that you would be better off dead, or of hurting yourself</question>
      </sub_questions>
    </question_group>
  </questions>
  <responses>
'''
    
    # Process each respondent in the JSON data (keep existing response structure)
    for respondent_data in json_data['responses']:
        respondent_id = respondent_data['respondent']
        answers = respondent_data['answers']
        
        xml_content += f'    <respondent id="{respondent_id}">\n'
        
        # Add individual answers and grouped answers
        for question, answer in answers.items():
            if isinstance(answer, dict):
                # Handle grouped questions
                xml_content += f'      <answer_group question="{question}">\n'
                for sub_question, sub_answer in answer.items():
                    xml_content += f'        <answer sub_question="{sub_question}">{sub_answer}</answer>\n'
                xml_content += f'      </answer_group>\n'
            else:
                # Handle simple questions
                xml_content += f'      <answer question="{question}">{answer}</answer>\n'
        
        xml_content += '    </respondent>\n'
    
    xml_content += '''  </responses>
</questionnaire>
'''
    
    return xml_content

def fix_xml_format(json_file_path, xml_file_path):
    """Fix XML file format using JSON as source"""
    
    # Read JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Generate properly formatted XML content
    fixed_content = generate_xml_from_json(json_data)
    
    # Write the fixed content
    with open(xml_file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    return True

def process_all_conceptual_aggregation_xml_files():
    """Process all XML files in conceptual_aggregation to match answer_lookup format"""
    json_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/conceptual_aggregation/json'
    xml_base_path = '/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/conceptual_aggregation/xml'
    
    if not os.path.exists(json_base_path):
        print(f"Error: JSON directory not found: {json_base_path}")
        return
    
    if not os.path.exists(xml_base_path):
        print(f"Error: XML directory not found: {xml_base_path}")
        return
    
    # Get all JSON files to use as source
    json_files = [f for f in os.listdir(json_base_path) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    processed_count = 0
    changes_made = 0
    
    for json_file in sorted(json_files):
        # Determine corresponding XML file
        xml_file = json_file.replace('.json', '.xml')
        json_file_path = os.path.join(json_base_path, json_file)
        xml_file_path = os.path.join(xml_base_path, xml_file)
        
        if not os.path.exists(xml_file_path):
            print(f"Warning: XML file not found: {xml_file}")
            continue
        
        # Fix the XML file using JSON data
        try:
            if fix_xml_format(json_file_path, xml_file_path):
                changes_made += 1
                print(f"Processing {xml_file}: Fixed format to match answer_lookup structure")
            else:
                print(f"Processing {xml_file}: No changes needed")
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")
        
        processed_count += 1
    
    print(f"\nProcessing complete!")
    print(f"- Total files processed: {processed_count}")
    print(f"- Files with changes: {changes_made}")
    print(f"- Files without changes: {processed_count - changes_made}")
    
    if changes_made > 0:
        print(f"\nSuccessfully standardized conceptual_aggregation XML format!")
        print(f"- Fixed question structure to use question_group with base_question and sub_questions")
        print(f"- Maintained existing response structure (already correct)")
        print(f"- XML format now matches answer_lookup hierarchical structure")
    else:
        print(f"\nAll XML files already had correct format.")

if __name__ == "__main__":
    process_all_conceptual_aggregation_xml_files()