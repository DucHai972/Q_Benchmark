#!/usr/bin/env python3
import json
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path


def generate_ttl_from_json(json_data):
    """Generate TTL content matching answer_lookup format"""
    lines = []
    
    # Header with modern format including qg namespace
    lines.extend([
        "@prefix : <http://example.org/survey#> .",
        "@prefix pred: <http://example.org/predicate#> .",
        "@prefix qg: <http://example.org/question_group#> .",
        "",
        "# Questions"
    ])
    
    # Individual questions
    lines.extend([
        ':QYear_of_birth pred:Text "What is your date of birth? [Open-ended]" .',
        ':QGender pred:Text "What is your gender? [MCQ: 1. Male 2. Female]" .',
        ':QSocio_economic_status pred:Text "What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]" .',
        ':QEthnic_identity pred:Text "According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]" .',
        ""
    ])
    
    # Question groups with hierarchical structure
    lines.extend([
        ':QGParental_Education pred:BaseQuestion "How many years of education did your parents receive? [Open-ended]" ;',
        '    qg:hasSubQuestion :QParental_Education_Father, :QParental_Education_Mother .',
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
        ':QGEmotional_Regulation_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is \'almost never\', 2 is \'sometimes\', 3 is \'fairly often\', and 4 is \'very often\', how often you experienced the following feelings during the last month: [Likert 0–4]" ;',
        '    qg:hasSubQuestion :QEmotional_Regulation_Frequency_Upset_by_Unexpected_Events,',
        '                      :QEmotional_Regulation_Frequency_Unable_to_Control_Important_Things,',
        '                      :QEmotional_Regulation_Frequency_Nervous_and_Stressed,',
        '                      :QEmotional_Regulation_Frequency_Lacked_Confidence_Handling_Problems,',
        '                      :QEmotional_Regulation_Frequency_Things_Going_Your_Way,',
        '                      :QEmotional_Regulation_Frequency_Unable_to_Cope,',
        '                      :QEmotional_Regulation_Frequency_Irritated_by_Life,',
        '                      :QEmotional_Regulation_Frequency_On_Top_of_Things,',
        '                      :QEmotional_Regulation_Frequency_Angered_by_Uncontrollable_Events,',
        '                      :QEmotional_Regulation_Frequency_Felt_Overwhelmed .',
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
        ':QGAnxiety_Symptoms_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is \'Not at all\', 1 is \'several days\', 2 is \'more than half of the days\', and 3 is \'Nearly every day\'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]" ;',
        '    qg:hasSubQuestion :QAnxiety_Symptoms_Frequency_Feeling_Nervous_or_On_Edge,',
        '                      :QAnxiety_Symptoms_Frequency_Uncontrollable_Worrying,',
        '                      :QAnxiety_Symptoms_Frequency_Excessive_Worry,',
        '                      :QAnxiety_Symptoms_Frequency_Trouble_Relaxing,',
        '                      :QAnxiety_Symptoms_Frequency_Restlessness,',
        '                      :QAnxiety_Symptoms_Frequency_Irritability,',
        '                      :QAnxiety_Symptoms_Frequency_Fear_Something_Awful_Might_Happen .',
        "",
        ':QAnxiety_Symptoms_Frequency_Feeling_Nervous_or_On_Edge pred:Text "Feeling nervous, anxious, or on edge" .',
        ':QAnxiety_Symptoms_Frequency_Uncontrollable_Worrying pred:Text "Not being able to stop or control worrying" .',
        ':QAnxiety_Symptoms_Frequency_Excessive_Worry pred:Text "Worrying too much about different things" .',
        ':QAnxiety_Symptoms_Frequency_Trouble_Relaxing pred:Text "Trouble relaxing" .',
        ':QAnxiety_Symptoms_Frequency_Restlessness pred:Text "Being so restless that it is hard to sit still" .',
        ':QAnxiety_Symptoms_Frequency_Irritability pred:Text "Becoming easily annoyed or irritable" .',
        ':QAnxiety_Symptoms_Frequency_Fear_Something_Awful_Might_Happen pred:Text "Feeling afraid, as if something awful might happen" .',
        "",
        ':QGDepressive_Symptoms_Frequency pred:BaseQuestion "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is \'Not at all\', 1 is \'several days\', 2 is \'more than half of the days\', and 3 is \'Nearly every day\'. Over the last two weeks, how often have you been bothered by the following problems?" ;',
        '    qg:hasSubQuestion :QDepressive_Symptoms_Frequency_Anhedonia,',
        '                      :QDepressive_Symptoms_Frequency_Depressed_Mood,',
        '                      :QDepressive_Symptoms_Frequency_Sleep_Problems,',
        '                      :QDepressive_Symptoms_Frequency_Fatigue,',
        '                      :QDepressive_Symptoms_Frequency_Appetite_Changes,',
        '                      :QDepressive_Symptoms_Frequency_Feelings_of_Worthlessness,',
        '                      :QDepressive_Symptoms_Frequency_Concentration_Difficulties,',
        '                      :QDepressive_Symptoms_Frequency_Psychomotor_Changes,',
        '                      :QDepressive_Symptoms_Frequency_Suicidal_Thoughts .',
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
    ])
    
    # Generate responses in hierarchical format
    responses = json_data.get("responses", [])
    
    for response in responses:
        respondent_id = response.get("respondent", "Unknown")
        resp_id = f"R{respondent_id}"
        answers = response.get("answers", {})
        
        # Basic responses
        lines.extend([
            f":{resp_id} pred:Year_of_birth {answers.get('Year of birth', 0.0)} ;",
            f"     pred:Gender {answers.get('Gender', 0.0)} ;",
            f"     pred:Socio_economic_status {answers.get('Socio-economic status', 0.0)} ;",
            f"     pred:Ethnic_identity {answers.get('Ethnic identity', 0.0)} .",
            ""
        ])
        
        # Parental Education group
        parental_edu = answers.get('Parental Education', {})
        if parental_edu:
            parental_lines = [f":{resp_id}_Parental_Education"]
            if 'Father' in parental_edu:
                parental_lines.append(f"                       pred:Father {parental_edu['Father']} ;")
            if 'Mother' in parental_edu:
                if 'Father' in parental_edu:
                    parental_lines[-1] = parental_lines[-1].rstrip(' ;') + ' ;'
                parental_lines.append(f"                       pred:Mother {parental_edu['Mother']} .")
            else:
                if parental_lines[-1].endswith(' ;'):
                    parental_lines[-1] = parental_lines[-1].rstrip(' ;') + ' .'
            
            lines.extend(parental_lines)
            lines.extend([
                f":{resp_id} pred:hasGroupResponse :{resp_id}_Parental_Education .",
                ""
            ])
        
        # Individual well-being responses
        lines.extend([
            f":{resp_id} pred:Life_satisfaction {answers.get('Life satisfaction', 0.0)} ;",
            f"     pred:Happiness {answers.get('Happiness', 0.0)} ;",
            f"     pred:Laughter {answers.get('Laughter', 0.0)} ;",
            f"     pred:Learning {answers.get('Learning', 0.0)} ;",
            f"     pred:Enjoyment {answers.get('Enjoyment', 0.0)} ;",
            f"     pred:Worry {answers.get('Worry', 0.0)} ;",
            f"     pred:Depression {answers.get('Depression', 0.0)} ;",
            f"     pred:Anger {answers.get('Anger', 0.0)} ;",
            f"     pred:Stress {answers.get('Stress', 0.0)} ;",
            f"     pred:Loneliness {answers.get('Loneliness', 0.0)} .",
            ""
        ])
        
        # Emotional Regulation Frequency group
        emo_reg = answers.get('Emotional Regulation Frequency', {})
        if emo_reg:
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
                if key in emo_reg:
                    entries.append(f"pred:{mapped_key} {emo_reg[key]}")
            
            for i, entry in enumerate(entries):
                emo_lines.append(f"                                   {entry} {'.' if i == len(entries) - 1 else ';'}")
            
            lines.extend(emo_lines)
            lines.extend([
                f":{resp_id} pred:hasGroupResponse :{resp_id}_Emotional_Regulation_Frequency .",
                ""
            ])
        
        # Anxiety Symptoms Frequency group
        anxiety = answers.get('Anxiety Symptoms Frequency', {})
        if anxiety:
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
                if key in anxiety:
                    entries.append(f"pred:{mapped_key} {anxiety[key]}")
            
            for i, entry in enumerate(entries):
                anxiety_lines.append(f"                               {entry} {'.' if i == len(entries) - 1 else ';'}")
            
            lines.extend(anxiety_lines)
            lines.extend([
                f":{resp_id} pred:hasGroupResponse :{resp_id}_Anxiety_Symptoms_Frequency .",
                ""
            ])
        
        # Depressive Symptoms Frequency group
        depression = answers.get('Depressive Symptoms Frequency', {})
        if depression:
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
                if key in depression:
                    entries.append(f"pred:{mapped_key} {depression[key]}")
            
            for i, entry in enumerate(entries):
                depression_lines.append(f"                                  {entry} {'.' if i == len(entries) - 1 else ';'}")
            
            lines.extend(depression_lines)
            lines.extend([
                f":{resp_id} pred:hasGroupResponse :{resp_id}_Depressive_Symptoms_Frequency .",
                ""
            ])
    
    return '\n'.join(lines)


def generate_txt_from_json(json_data):
    """Generate TXT content matching answer_lookup format with hierarchical structure"""
    lines = []
    
    lines.extend([
        "Survey Data",
        "==================================================",
        "",
        "Questions:"
    ])
    
    question_num = 1
    
    # Individual questions
    lines.extend([
        f"{question_num}. Year of birth: What is your date of birth? [Open-ended]",
        f"{question_num + 1}. Gender: What is your gender? [MCQ: 1. Male 2. Female]",
        f"{question_num + 2}. Socio-economic status: What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]",
        f"{question_num + 3}. Ethnic identity: According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]",
        f"{question_num + 4}. Parental Education: How many years of education did your parents receive? [Open-ended]",
        "   - Father: Father?",
        "   - Mother: Mother?"
    ])
    question_num += 5
    
    # Individual well-being questions
    wellbeing_questions = [
        "Life satisfaction: In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]",
        "Happiness: How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Laughter: How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Learning: Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Enjoyment: How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Worry: How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Depression: How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Anger: How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Stress: How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Loneliness: How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"
    ]
    
    for q in wellbeing_questions:
        lines.append(f"{question_num}. {q}")
        question_num += 1
    
    # Grouped questions
    lines.append(f"{question_num}. Emotional Regulation Frequency: Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]")
    
    emo_reg_subs = [
        "Upset by Unexpected Events: how often have you been upset because of something that happened unexpectedly?",
        "Unable to Control Important Things: how often have you felt that you were unable to control the important things in your life?",
        "Nervous and Stressed: how often have you felt nervous and stressed?",
        "Lacked Confidence Handling Problems: how often have you felt confident about your ability to handle your personal problems?",
        "Things Going Your Way: how often have you felt that things were going your way?",
        "Unable to Cope: how often have you found that you could not cope with all the things that you had to do?",
        "Irritated by Life: how often have you been able to control irritations in your life?",
        "On Top of Things: how often have you felt that you were on top of things?",
        "Angered by Uncontrollable Events: how often have you been angered because of things that happened that were outside of your control?",
        "Felt Overwhelmed: how often have you felt difficulties were piling up so high that you could not overcome them?"
    ]
    
    for sub in emo_reg_subs:
        lines.append(f"    - {sub}")
    
    question_num += 1
    
    lines.append(f"{question_num}. Anxiety Symptoms Frequency: Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]")
    
    anxiety_subs = [
        "Feeling Nervous or On Edge: Feeling nervous, anxious, or on edge",
        "Uncontrollable Worrying: Not being able to stop or control worrying",
        "Excessive Worry: Worrying too much about different things",
        "Trouble Relaxing: Trouble relaxing",
        "Restlessness: Being so restless that it is hard to sit still",
        "Irritability: Becoming easily annoyed or irritable",
        "Fear Something Awful Might Happen: Feeling afraid, as if something awful might happen"
    ]
    
    for sub in anxiety_subs:
        lines.append(f"    - {sub}")
    
    question_num += 1
    
    lines.append(f"{question_num}. Depressive Symptoms Frequency: Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems?")
    
    depression_subs = [
        "Anhedonia: Little interest or pleasure in doing things",
        "Depressed Mood: Feeling down, depressed, or hopeless",
        "Sleep Problems: Trouble falling or staying asleep, or sleeping too much",
        "Fatigue: Feeling tired or having little energy",
        "Appetite Changes: Poor appetite or overeating",
        "Feelings of Worthlessness: Feeling bad about yourself or that you are a failure or have let yourself or your family down",
        "Concentration Difficulties: Trouble concentrating on things, such as reading the newspaper or watching television",
        "Psychomotor Changes: Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
        "Suicidal Thoughts: Thoughts that you would be better off dead, or of hurting yourself"
    ]
    
    for sub in depression_subs:
        lines.append(f"    - {sub}")
    
    # Responses section
    lines.extend(["", "Responses:", "=================================================="])
    
    responses = json_data.get("responses", [])
    for response in responses:
        respondent_id = response.get("respondent", "Unknown")
        answers = response.get("answers", {})
        
        lines.extend([
            "",
            f"Respondent {respondent_id}:",
            "-" * 30
        ])
        
        # Basic responses
        lines.extend([
            f"Year of birth: {answers.get('Year of birth', 'N/A')}",
            f"Gender: {answers.get('Gender', 'N/A')}",
            f"Socio-economic status: {answers.get('Socio-economic status', 'N/A')}",
            f"Ethnic identity: {answers.get('Ethnic identity', 'N/A')}"
        ])
        
        # Parental Education
        parental_edu = answers.get('Parental Education', {})
        if parental_edu:
            lines.append("Parental Education:")
            if 'Father' in parental_edu:
                lines.append(f"  - Father: {parental_edu['Father']}")
            if 'Mother' in parental_edu:
                lines.append(f"  - Mother: {parental_edu['Mother']}")
        
        # Individual well-being responses
        wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment', 
                           'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
        for field in wellbeing_fields:
            lines.append(f"{field}: {answers.get(field, 'N/A')}")
        
        # Grouped responses
        emo_reg = answers.get('Emotional Regulation Frequency', {})
        if emo_reg:
            lines.append("Emotional Regulation Frequency:")
            for key, value in emo_reg.items():
                lines.append(f"  - {key}: {value}")
        
        anxiety = answers.get('Anxiety Symptoms Frequency', {})
        if anxiety:
            lines.append("Anxiety Symptoms Frequency:")
            for key, value in anxiety.items():
                lines.append(f"  - {key}: {value}")
        
        depression = answers.get('Depressive Symptoms Frequency', {})
        if depression:
            lines.append("Depressive Symptoms Frequency:")
            for key, value in depression.items():
                lines.append(f"  - {key}: {value}")
    
    return '\n'.join(lines)


def generate_xml_from_json(json_data):
    """Generate XML content matching answer_lookup format"""
    root = ET.Element("SurveyData")
    
    # Questions section
    questions_elem = ET.SubElement(root, "Questions")
    
    # Individual questions
    individual_questions = [
        ("Year of birth", "What is your date of birth? [Open-ended]"),
        ("Gender", "What is your gender? [MCQ: 1. Male 2. Female]"),
        ("Socio-economic status", "What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]"),
        ("Ethnic identity", "According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]")
    ]
    
    for name, text in individual_questions:
        q_elem = ET.SubElement(questions_elem, "Question", name=name)
        q_elem.text = text
    
    # Grouped questions
    # Parental Education
    parental_group = ET.SubElement(questions_elem, "QuestionGroup", name="Parental Education")
    parental_base = ET.SubElement(parental_group, "BaseQuestion")
    parental_base.text = "How many years of education did your parents receive? [Open-ended]"
    parental_father = ET.SubElement(parental_group, "SubQuestion", name="Father")
    parental_father.text = "Father?"
    parental_mother = ET.SubElement(parental_group, "SubQuestion", name="Mother") 
    parental_mother.text = "Mother?"
    
    # Individual well-being questions
    wellbeing_questions = [
        ("Life satisfaction", "In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]"),
        ("Happiness", "How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Laughter", "How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Learning", "Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Enjoyment", "How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Worry", "How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Depression", "How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Anger", "How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Stress", "How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Loneliness", "How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]")
    ]
    
    for name, text in wellbeing_questions:
        q_elem = ET.SubElement(questions_elem, "Question", name=name)
        q_elem.text = text
    
    # Emotional Regulation Frequency group
    emo_group = ET.SubElement(questions_elem, "QuestionGroup", name="Emotional Regulation Frequency")
    emo_base = ET.SubElement(emo_group, "BaseQuestion")
    emo_base.text = "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]"
    
    emo_subs = [
        ("Upset by Unexpected Events", "how often have you been upset because of something that happened unexpectedly?"),
        ("Unable to Control Important Things", "how often have you felt that you were unable to control the important things in your life?"),
        ("Nervous and Stressed", "how often have you felt nervous and stressed?"),
        ("Lacked Confidence Handling Problems", "how often have you felt confident about your ability to handle your personal problems?"),
        ("Things Going Your Way", "how often have you felt that things were going your way?"),
        ("Unable to Cope", "how often have you found that you could not cope with all the things that you had to do?"),
        ("Irritated by Life", "how often have you been able to control irritations in your life?"),
        ("On Top of Things", "how often have you felt that you were on top of things?"),
        ("Angered by Uncontrollable Events", "how often have you been angered because of things that happened that were outside of your control?"),
        ("Felt Overwhelmed", "how often have you felt difficulties were piling up so high that you could not overcome them?")
    ]
    
    for name, text in emo_subs:
        sub_elem = ET.SubElement(emo_group, "SubQuestion", name=name)
        sub_elem.text = text
    
    # Anxiety group
    anxiety_group = ET.SubElement(questions_elem, "QuestionGroup", name="Anxiety Symptoms Frequency")
    anxiety_base = ET.SubElement(anxiety_group, "BaseQuestion")
    anxiety_base.text = "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]"
    
    anxiety_subs = [
        ("Feeling Nervous or On Edge", "Feeling nervous, anxious, or on edge"),
        ("Uncontrollable Worrying", "Not being able to stop or control worrying"),
        ("Excessive Worry", "Worrying too much about different things"),
        ("Trouble Relaxing", "Trouble relaxing"),
        ("Restlessness", "Being so restless that it is hard to sit still"),
        ("Irritability", "Becoming easily annoyed or irritable"),
        ("Fear Something Awful Might Happen", "Feeling afraid, as if something awful might happen")
    ]
    
    for name, text in anxiety_subs:
        sub_elem = ET.SubElement(anxiety_group, "SubQuestion", name=name)
        sub_elem.text = text
    
    # Depression group
    depression_group = ET.SubElement(questions_elem, "QuestionGroup", name="Depressive Symptoms Frequency")
    depression_base = ET.SubElement(depression_group, "BaseQuestion")
    depression_base.text = "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems?"
    
    depression_subs = [
        ("Anhedonia", "Little interest or pleasure in doing things"),
        ("Depressed Mood", "Feeling down, depressed, or hopeless"),
        ("Sleep Problems", "Trouble falling or staying asleep, or sleeping too much"),
        ("Fatigue", "Feeling tired or having little energy"),
        ("Appetite Changes", "Poor appetite or overeating"),
        ("Feelings of Worthlessness", "Feeling bad about yourself or that you are a failure or have let yourself or your family down"),
        ("Concentration Difficulties", "Trouble concentrating on things, such as reading the newspaper or watching television"),
        ("Psychomotor Changes", "Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual"),
        ("Suicidal Thoughts", "Thoughts that you would be better off dead, or of hurting yourself")
    ]
    
    for name, text in depression_subs:
        sub_elem = ET.SubElement(depression_group, "SubQuestion", name=name)
        sub_elem.text = text
    
    # Responses section
    responses_elem = ET.SubElement(root, "Responses")
    
    responses = json_data.get("responses", [])
    for response in responses:
        respondent_id = response.get("respondent", "Unknown")
        answers = response.get("answers", {})
        
        resp_elem = ET.SubElement(responses_elem, "Respondent", id=respondent_id)
        
        # Basic responses
        basic_fields = ['Year of birth', 'Gender', 'Socio-economic status', 'Ethnic identity']
        for field in basic_fields:
            if field in answers:
                answer_elem = ET.SubElement(resp_elem, "Answer", question=field)
                answer_elem.text = str(answers[field])
        
        # Parental Education
        parental_edu = answers.get('Parental Education', {})
        if parental_edu:
            group_elem = ET.SubElement(resp_elem, "GroupAnswer", question="Parental Education")
            for key, value in parental_edu.items():
                sub_elem = ET.SubElement(group_elem, "SubAnswer", question=key)
                sub_elem.text = str(value)
        
        # Individual well-being responses
        wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment', 
                           'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
        for field in wellbeing_fields:
            if field in answers:
                answer_elem = ET.SubElement(resp_elem, "Answer", question=field)
                answer_elem.text = str(answers[field])
        
        # Grouped responses
        grouped_fields = ['Emotional Regulation Frequency', 'Anxiety Symptoms Frequency', 'Depressive Symptoms Frequency']
        for field in grouped_fields:
            if field in answers and answers[field]:
                group_elem = ET.SubElement(resp_elem, "GroupAnswer", question=field)
                for key, value in answers[field].items():
                    sub_elem = ET.SubElement(group_elem, "SubAnswer", question=key)
                    sub_elem.text = str(value)
    
    # Convert to pretty XML string
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")[23:]  # Remove first line


def generate_md_from_json(json_data):
    """Generate Markdown content matching answer_lookup format"""
    lines = []
    
    lines.extend([
        "# Survey Data",
        "",
        "## Questions",
        ""
    ])
    
    # Individual questions
    lines.extend([
        "1. **Year of birth:** What is your date of birth? [Open-ended]",
        "2. **Gender:** What is your gender? [MCQ: 1. Male 2. Female]", 
        "3. **Socio-economic status:** What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]",
        "4. **Ethnic identity:** According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]",
        "5. **Parental Education:** How many years of education did your parents receive? [Open-ended]",
        "   - **Father:** Father?",
        "   - **Mother:** Mother?",
        ""
    ])
    
    # Individual well-being questions
    question_num = 6
    wellbeing_questions = [
        ("Life satisfaction", "In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]"),
        ("Happiness", "How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Laughter", "How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Learning", "Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Enjoyment", "How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Worry", "How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Depression", "How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Anger", "How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Stress", "How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]"),
        ("Loneliness", "How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]")
    ]
    
    for name, text in wellbeing_questions:
        lines.append(f"{question_num}. **{name}:** {text}")
        question_num += 1
    
    lines.append("")
    
    # Grouped questions
    lines.append(f"{question_num}. **Emotional Regulation Frequency:** Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]")
    
    emo_reg_subs = [
        ("Upset by Unexpected Events", "how often have you been upset because of something that happened unexpectedly?"),
        ("Unable to Control Important Things", "how often have you felt that you were unable to control the important things in your life?"),
        ("Nervous and Stressed", "how often have you felt nervous and stressed?"),
        ("Lacked Confidence Handling Problems", "how often have you felt confident about your ability to handle your personal problems?"),
        ("Things Going Your Way", "how often have you felt that things were going your way?"),
        ("Unable to Cope", "how often have you found that you could not cope with all the things that you had to do?"),
        ("Irritated by Life", "how often have you been able to control irritations in your life?"),
        ("On Top of Things", "how often have you felt that you were on top of things?"),
        ("Angered by Uncontrollable Events", "how often have you been angered because of things that happened that were outside of your control?"),
        ("Felt Overwhelmed", "how often have you felt difficulties were piling up so high that you could not overcome them?")
    ]
    
    for name, text in emo_reg_subs:
        lines.append(f"   - **{name}:** {text}")
    
    question_num += 1
    lines.append("")
    
    lines.append(f"{question_num}. **Anxiety Symptoms Frequency:** Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]")
    
    anxiety_subs = [
        ("Feeling Nervous or On Edge", "Feeling nervous, anxious, or on edge"),
        ("Uncontrollable Worrying", "Not being able to stop or control worrying"),
        ("Excessive Worry", "Worrying too much about different things"),
        ("Trouble Relaxing", "Trouble relaxing"),
        ("Restlessness", "Being so restless that it is hard to sit still"),
        ("Irritability", "Becoming easily annoyed or irritable"),
        ("Fear Something Awful Might Happen", "Feeling afraid, as if something awful might happen")
    ]
    
    for name, text in anxiety_subs:
        lines.append(f"   - **{name}:** {text}")
    
    question_num += 1
    lines.append("")
    
    lines.append(f"{question_num}. **Depressive Symptoms Frequency:** Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems?")
    
    depression_subs = [
        ("Anhedonia", "Little interest or pleasure in doing things"),
        ("Depressed Mood", "Feeling down, depressed, or hopeless"),
        ("Sleep Problems", "Trouble falling or staying asleep, or sleeping too much"),
        ("Fatigue", "Feeling tired or having little energy"),
        ("Appetite Changes", "Poor appetite or overeating"),
        ("Feelings of Worthlessness", "Feeling bad about yourself or that you are a failure or have let yourself or your family down"),
        ("Concentration Difficulties", "Trouble concentrating on things, such as reading the newspaper or watching television"),
        ("Psychomotor Changes", "Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual"),
        ("Suicidal Thoughts", "Thoughts that you would be better off dead, or of hurting yourself")
    ]
    
    for name, text in depression_subs:
        lines.append(f"   - **{name}:** {text}")
    
    # Responses section
    lines.extend(["", "", "## Responses", ""])
    
    responses = json_data.get("responses", [])
    for response in responses:
        respondent_id = response.get("respondent", "Unknown")
        answers = response.get("answers", {})
        
        lines.extend([
            f"### Respondent {respondent_id}",
            ""
        ])
        
        # Basic responses
        basic_fields = ['Year of birth', 'Gender', 'Socio-economic status', 'Ethnic identity']
        for field in basic_fields:
            if field in answers:
                lines.append(f"- **{field}:** {answers[field]}")
        
        # Parental Education
        parental_edu = answers.get('Parental Education', {})
        if parental_edu:
            lines.append("- **Parental Education:**")
            for key, value in parental_edu.items():
                lines.append(f"  - **{key}:** {value}")
        
        # Individual well-being responses
        wellbeing_fields = ['Life satisfaction', 'Happiness', 'Laughter', 'Learning', 'Enjoyment', 
                           'Worry', 'Depression', 'Anger', 'Stress', 'Loneliness']
        for field in wellbeing_fields:
            if field in answers:
                lines.append(f"- **{field}:** {answers[field]}")
        
        # Grouped responses
        grouped_fields = ['Emotional Regulation Frequency', 'Anxiety Symptoms Frequency', 'Depressive Symptoms Frequency']
        for field in grouped_fields:
            if field in answers and answers[field]:
                lines.append(f"- **{field}:**")
                for key, value in answers[field].items():
                    lines.append(f"  - **{key}:** {value}")
        
        lines.append("")
    
    return '\n'.join(lines)


def standardize_formats(json_file_path, output_dir):
    """Standardize all formats using JSON data"""
    
    # Read JSON data
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    
    case_name = Path(json_file_path).stem
    
    # Generate and write TTL
    ttl_content = generate_ttl_from_json(json_data)
    ttl_path = output_dir / "ttl" / f"{case_name}.ttl"
    with open(ttl_path, 'w') as f:
        f.write(ttl_content)
    
    # Generate and write TXT
    txt_content = generate_txt_from_json(json_data)
    txt_path = output_dir / "txt" / f"{case_name}.txt"
    with open(txt_path, 'w') as f:
        f.write(txt_content)
    
    # Generate and write XML
    xml_content = generate_xml_from_json(json_data)
    xml_path = output_dir / "xml" / f"{case_name}.xml"
    with open(xml_path, 'w') as f:
        f.write(xml_content)
    
    # Generate and write MD
    md_content = generate_md_from_json(json_data)
    md_path = output_dir / "md" / f"{case_name}.md"
    with open(md_path, 'w') as f:
        f.write(md_content)


def main():
    base_dir = Path("/insight-fast/dnguyen/Q_Benchmark/benchmark_cache/self-reported-mental-health/rule_based_querying")
    json_dir = base_dir / "json"
    
    # Get all JSON files
    json_files = list(json_dir.glob("case_*.json"))
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        print(f"Standardizing formats for {json_file.name}...")
        try:
            standardize_formats(json_file, base_dir)
            print(f"✓ Successfully standardized {json_file.name}")
        except Exception as e:
            print(f"✗ Error standardizing {json_file.name}: {e}")
    
    print("Format standardization complete!")


if __name__ == "__main__":
    main()