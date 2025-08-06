#!/usr/bin/env python3
import re
import os
import ast
from pathlib import Path


def parse_dict_string(dict_str):
    """Parse dictionary-like string into Python dict"""
    try:
        # Remove quotes around the dictionary string
        clean_str = dict_str.strip('"\'')
        # Use ast.literal_eval for safe evaluation
        return ast.literal_eval(clean_str)
    except:
        return {}


def parse_ttl_responses(content):
    """Parse TTL content and extract respondent data"""
    lines = content.split('\n')
    respondents = {}
    current_respondent = None
    current_data = {}
    
    for line in lines:
        line = line.strip()
        
        # Start of a new respondent
        if line.startswith(':Respondent') and ' a :Person' in line:
            if current_respondent:
                respondents[current_respondent] = current_data
            
            current_respondent = line.split(' ')[0].replace(':Respondent', 'R')
            current_data = {}
            
        # Parse data lines
        elif current_respondent and line.startswith('pred:'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                pred_part = parts[0].replace('pred:', '')
                value_part = parts[1].rstrip(' ;.')
                current_data[pred_part] = value_part
    
    # Don't forget the last respondent
    if current_respondent:
        respondents[current_respondent] = current_data
    
    return respondents


def transform_ttl_file(input_file, output_file):
    """Transform TTL file from original to modified format"""
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    output_lines = []
    
    # Add prefixes
    output_lines.extend([
        "@prefix : <http://example.org/survey#> .",
        "@prefix pred: <http://example.org/predicate#> .",
        "@prefix qg: <http://example.org/question_group#> .",
        "",
        "# Questions"
    ])
    
    # Add individual questions (non-grouped)
    individual_questions = [
        ':QYear_of_birth pred:Text "What is your date of birth? [Open-ended]" .',
        ':QGender pred:Text "What is your gender? [MCQ: 1. Male 2. Female]" .',
        ':QSocio_economic_status pred:Text "What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]" .',
        ':QEthnic_identity pred:Text "According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]" .',
        ""
    ]
    output_lines.extend(individual_questions)
    
    # Add grouped questions
    grouped_questions = [
        "# Parental Education Question Group",
        ':QGParental_Education pred:BaseQuestion "How many years of education did your parents receive? [Open-ended]" ;',
        "    qg:hasSubQuestion :QParental_Education_Father, :QParental_Education_Mother .",
        ':QParental_Education_Father pred:Text "Father?" .',
        ':QParental_Education_Mother pred:Text "Mother?" .',
        "",
        ':QLife_satisfaction pred:Text "In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]" .',
        ':QHappiness pred:Text "How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QLaughter pred:Text "How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QLearning pred:Text "Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QEnjoyment pred:Text "How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QWorry pred:Text "How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QDepression pred:Text "How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QAnger pred:Text "How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QStress pred:Text "How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        ':QLoneliness pred:Text "How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]" .',
        "",
        "# Emotional Regulation Frequency Question Group",
        ':QGEmotional_Regulation_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is \'almost never\', 2 is \'sometimes\', 3 is \'fairly often\', and 4 is \'very often\', how often you experienced the following feelings during the last month: [Likert 0–4]" ;',
        "    qg:hasSubQuestion :QEmotional_Regulation_Frequency_Upset_by_Unexpected_Events,",
        "                      :QEmotional_Regulation_Frequency_Unable_to_Control_Important_Things,",
        "                      :QEmotional_Regulation_Frequency_Nervous_and_Stressed,",
        "                      :QEmotional_Regulation_Frequency_Lacked_Confidence_Handling_Problems,",
        "                      :QEmotional_Regulation_Frequency_Things_Going_Your_Way,",
        "                      :QEmotional_Regulation_Frequency_Unable_to_Cope,",
        "                      :QEmotional_Regulation_Frequency_Irritated_by_Life,",
        "                      :QEmotional_Regulation_Frequency_On_Top_of_Things,",
        "                      :QEmotional_Regulation_Frequency_Angered_by_Uncontrollable_Events,",
        "                      :QEmotional_Regulation_Frequency_Felt_Overwhelmed .",
        "",
        ':QEmotional_Regulation_Frequency_Upset_by_Unexpected_Events pred:Text "how often have you been upset because of something that happened unexpectedly?" .',
        ':QEmotional_Regulation_Frequency_Unable_to_Control_Important_Things pred:Text "how often have you felt that you were unable to control the important things in your life?" .',
        ':QEmotional_Regulation_Frequency_Nervous_and_Stressed pred:Text "how often have you felt nervous and stressed?" .',
        ':QEmotional_Regulation_Frequency_Lacked_Confidence_Handling_Problems pred:Text "how often have you felt confident about your ability to handle your personal problems?" .',
        ':QEmotional_Regulation_Frequency_Things_Going_Your_Way pred:Text "how often have you felt that things were going your way?" .',
        ':QEmotional_Regulation_Frequency_Unable_to_Cope pred:Text "how often have you found that you could not cope with all the things that you had to do?" .',
        ':QEmotional_Regulation_Frequency_Irritated_by_Life pred:Text "how often have you been able to control irritations in your life?" .',
        ':QEmotional_Regulation_Frequency_On_Top_of_Things pred:Text "how often have you felt that you were on top of things?" .',
        ':QEmotional_Regulation_Frequency_Angered_by_Uncontrollable_Events pred:Text "how often have you been angered because of things that happened that were outside of your control?" .',
        ':QEmotional_Regulation_Frequency_Felt_Overwhelmed pred:Text "how often have you felt difficulties were piling up so high that you could not overcome them?" .',
        "",
        "# Anxiety Symptoms Frequency Question Group",
        ':QGAnxiety_Symptoms_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is \'Not at all\', 1 is \'several days\', 2 is \'more than half of the days\', and 3 is \'Nearly every day\'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]" ;',
        "    qg:hasSubQuestion :QAnxiety_Symptoms_Frequency_Feeling_Nervous_or_On_Edge,",
        "                      :QAnxiety_Symptoms_Frequency_Uncontrollable_Worrying,",
        "                      :QAnxiety_Symptoms_Frequency_Excessive_Worry,",
        "                      :QAnxiety_Symptoms_Frequency_Trouble_Relaxing,",
        "                      :QAnxiety_Symptoms_Frequency_Restlessness,",
        "                      :QAnxiety_Symptoms_Frequency_Irritability,",
        "                      :QAnxiety_Symptoms_Frequency_Fear_Something_Awful_Might_Happen .",
        "",
        ':QAnxiety_Symptoms_Frequency_Feeling_Nervous_or_On_Edge pred:Text "Feeling nervous, anxious, or on edge" .',
        ':QAnxiety_Symptoms_Frequency_Uncontrollable_Worrying pred:Text "Not being able to stop or control worrying" .',
        ':QAnxiety_Symptoms_Frequency_Excessive_Worry pred:Text "Worrying too much about different things" .',
        ':QAnxiety_Symptoms_Frequency_Trouble_Relaxing pred:Text "Trouble relaxing" .',
        ':QAnxiety_Symptoms_Frequency_Restlessness pred:Text "Being so restless that it is hard to sit still" .',
        ':QAnxiety_Symptoms_Frequency_Irritability pred:Text "Becoming easily annoyed or irritable" .',
        ':QAnxiety_Symptoms_Frequency_Fear_Something_Awful_Might_Happen pred:Text "Feeling afraid, as if something awful might happen" .',
        "",
        "# Depressive Symptoms Frequency Question Group",
        ':QGDepressive_Symptoms_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is \'Not at all\', 1 is \'several days\', 2 is \'more than half of the days\', and 3 is \'Nearly every day\'. Over the last two weeks, how often have you been bothered by the following problems?" ;',
        "    qg:hasSubQuestion :QDepressive_Symptoms_Frequency_Anhedonia,",
        "                      :QDepressive_Symptoms_Frequency_Depressed_Mood,",
        "                      :QDepressive_Symptoms_Frequency_Sleep_Problems,",
        "                      :QDepressive_Symptoms_Frequency_Fatigue,",
        "                      :QDepressive_Symptoms_Frequency_Appetite_Changes,",
        "                      :QDepressive_Symptoms_Frequency_Feelings_of_Worthlessness,",
        "                      :QDepressive_Symptoms_Frequency_Concentration_Difficulties,",
        "                      :QDepressive_Symptoms_Frequency_Psychomotor_Changes,",
        "                      :QDepressive_Symptoms_Frequency_Suicidal_Thoughts .",
        "",
        ':QDepressive_Symptoms_Frequency_Anhedonia pred:Text "Little interest or pleasure in doing things" .',
        ':QDepressive_Symptoms_Frequency_Depressed_Mood pred:Text "Feeling down, depressed, or hopeless" .',
        ':QDepressive_Symptoms_Frequency_Sleep_Problems pred:Text "Trouble falling or staying asleep, or sleeping too much" .',
        ':QDepressive_Symptoms_Frequency_Fatigue pred:Text "Feeling tired or having little energy" .',
        ':QDepressive_Symptoms_Frequency_Appetite_Changes pred:Text "Poor appetite or overeating" .',
        ':QDepressive_Symptoms_Frequency_Feelings_of_Worthlessness pred:Text "Feeling bad about yourself or that you are a failure or have let yourself or your family down" .',
        ':QDepressive_Symptoms_Frequency_Concentration_Difficulties pred:Text "Trouble concentrating on things, such as reading the newspaper or watching television" .',
        ':QDepressive_Symptoms_Frequency_Psychomotor_Changes pred:Text "Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual" .',
        ':QDepressive_Symptoms_Frequency_Suicidal_Thoughts pred:Text "Thoughts that you would be better off dead, or of hurting yourself" .',
        "",
        "# Responses"
    ]
    output_lines.extend(grouped_questions)
    
    # Parse and transform response data
    respondent_data = parse_ttl_responses(content)
    
    # Generate transformed response data
    for resp_id, data in respondent_data.items():
        # Individual basic responses
        basic_values = []
        quote_char = '"'
        basic_values.append(f":{resp_id} pred:Year_of_birth {data.get('Year_of_birth', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        basic_values.append(f"     pred:Gender {data.get('Gender', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        basic_values.append(f"     pred:Socio_economic_status {data.get('Socio_economic_status', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        basic_values.append(f"     pred:Ethnic_identity {data.get('Ethnic_identity', quote_char + '0.0' + quote_char).strip(quote_char)} .")
        basic_values.append("")
        
        output_lines.extend(basic_values)
        
        # Parental Education group
        parental_edu = data.get('Parental_Education', '{}')
        if parental_edu != '{}':
            parental_dict = parse_dict_string(parental_edu)
            if parental_dict:  # Only if we successfully parsed data
                parental_lines = [f":{resp_id}_Parental_Education"]
                entries = []
                
                if 'Father' in parental_dict:
                    entries.append(f"pred:Father {parental_dict['Father']}")
                if 'Mother' in parental_dict:
                    entries.append(f"pred:Mother {parental_dict['Mother']}")
                
                if entries:
                    for i, entry in enumerate(entries):
                        if i == 0:
                            parental_lines.append(f"                       {entry} {'.' if i == len(entries) - 1 else ';'}")
                        else:
                            parental_lines.append(f"                       {entry} {'.' if i == len(entries) - 1 else ';'}")
                    
                    output_lines.extend(parental_lines)
                    output_lines.append(f":{resp_id} pred:hasGroupResponse :{resp_id}_Parental_Education .")
                    output_lines.append("")
        
        # Individual well-being responses
        wellbeing_values = []
        wellbeing_values.append(f":{resp_id} pred:Life_satisfaction {data.get('Life_satisfaction', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Happiness {data.get('Happiness', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Laughter {data.get('Laughter', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Learning {data.get('Learning', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Enjoyment {data.get('Enjoyment', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Worry {data.get('Worry', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Depression {data.get('Depression', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Anger {data.get('Anger', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Stress {data.get('Stress', quote_char + '0.0' + quote_char).strip(quote_char)} ;")
        wellbeing_values.append(f"     pred:Loneliness {data.get('Loneliness', quote_char + '0.0' + quote_char).strip(quote_char)} .")
        wellbeing_values.append("")
        
        output_lines.extend(wellbeing_values)
        
        # Emotional Regulation Frequency group
        emo_reg = data.get('Emotional_Regulation_Frequency', '{}')
        if emo_reg != '{}':
            emo_dict = parse_dict_string(emo_reg)
            if emo_dict:  # Only if we successfully parsed data
                emo_lines = [f":{resp_id}_Emotional_Regulation_Frequency"]
                
                field_mapping = {
                    'Upset by Unexpected Events': 'Upset_by_Unexpected_Events',
                    'Unable to Control Important Things': 'Unable_to_Control_Important_Things',
                    'Lacked Confidence Handling Problems': 'Lacked_Confidence_Handling_Problems',
                    'Unable to Cope': 'Unable_to_Cope',
                    'Irritated by Life': 'Irritated_by_Life',
                    'On Top of Things': 'On_Top_of_Things'
                }
                
                entries = []
                for key, mapped_key in field_mapping.items():
                    if key in emo_dict:
                        entries.append(f"pred:{mapped_key} {emo_dict[key]}")
                
                if entries:
                    for i, entry in enumerate(entries):
                        emo_lines.append(f"                                   {entry} {'.' if i == len(entries) - 1 else ';'}")
                    
                    output_lines.extend(emo_lines)
                    output_lines.append(f":{resp_id} pred:hasGroupResponse :{resp_id}_Emotional_Regulation_Frequency .")
                    output_lines.append("")
        
        # Anxiety Symptoms Frequency group
        anxiety = data.get('Anxiety_Symptoms_Frequency', '{}')
        if anxiety != '{}':
            anxiety_dict = parse_dict_string(anxiety)
            if anxiety_dict:  # Only if we successfully parsed data
                anxiety_lines = [f":{resp_id}_Anxiety_Symptoms_Frequency"]
                
                field_mapping = {
                    'Feeling Nervous or On Edge': 'Feeling_Nervous_or_On_Edge',
                    'Trouble Relaxing': 'Trouble_Relaxing',
                    'Restlessness': 'Restlessness',
                    'Irritability': 'Irritability',
                    'Fear Something Awful Might Happen': 'Fear_Something_Awful_Might_Happen'
                }
                
                entries = []
                for key, mapped_key in field_mapping.items():
                    if key in anxiety_dict:
                        entries.append(f"pred:{mapped_key} {anxiety_dict[key]}")
                
                if entries:
                    for i, entry in enumerate(entries):
                        anxiety_lines.append(f"                               {entry} {'.' if i == len(entries) - 1 else ';'}")
                    
                    output_lines.extend(anxiety_lines)
                    output_lines.append(f":{resp_id} pred:hasGroupResponse :{resp_id}_Anxiety_Symptoms_Frequency .")
                    output_lines.append("")
        
        # Depressive Symptoms Frequency group
        depression = data.get('Depressive_Symptoms_Frequency', '{}')
        if depression != '{}':
            depression_dict = parse_dict_string(depression)
            if depression_dict:  # Only if we successfully parsed data
                depression_lines = [f":{resp_id}_Depressive_Symptoms_Frequency"]
                
                field_mapping = {
                    'Anhedonia': 'Anhedonia',
                    'Sleep Problems': 'Sleep_Problems',
                    'Fatigue': 'Fatigue',
                    'Appetite Changes': 'Appetite_Changes',
                    'Feelings of Worthlessness': 'Feelings_of_Worthlessness',
                    'Concentration Difficulties': 'Concentration_Difficulties',
                    'Suicidal Thoughts': 'Suicidal_Thoughts'
                }
                
                entries = []
                for key, mapped_key in field_mapping.items():
                    if key in depression_dict:
                        entries.append(f"pred:{mapped_key} {depression_dict[key]}")
                
                if entries:
                    for i, entry in enumerate(entries):
                        depression_lines.append(f"                                  {entry} {'.' if i == len(entries) - 1 else ';'}")
                    
                    output_lines.extend(depression_lines)
                    output_lines.append(f":{resp_id} pred:hasGroupResponse :{resp_id}_Depressive_Symptoms_Frequency .")
                    output_lines.append("")
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))


def main():
    ttl_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/answer_lookup/ttl")
    
    # Get all TTL files except case_1_modified.ttl
    ttl_files = [f for f in ttl_dir.glob("case_*.ttl") if not f.name.endswith("_modified.ttl")]
    
    print(f"Found {len(ttl_files)} TTL files to transform")
    
    for ttl_file in ttl_files:
        print(f"Transforming {ttl_file.name}...")
        try:
            transform_ttl_file(ttl_file, ttl_file)
            print(f"✓ Successfully transformed {ttl_file.name}")
        except Exception as e:
            print(f"✗ Error transforming {ttl_file.name}: {e}")
    
    print("Transformation complete!")


if __name__ == "__main__":
    main()