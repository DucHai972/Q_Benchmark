#!/usr/bin/env python3
import re

# Test MCQ parsing
question_text = "What is your insurance provider? [MCQ: A. Aetna B. Blue Cross C. Cigna D. Medicare E. UnitedHealthcare]"
print(f"Question: {question_text}")

# Extract MCQ options using regex
mcq_pattern = r'\[MCQ: (.+?)\]'
match = re.search(mcq_pattern, question_text)

if match:
    options_text = match.group(1)
    print(f"Options text: {options_text}")
    
    # Parse options like "A. Aetna B. Blue Cross C. Cigna D. Medicare E. UnitedHealthcare"
    options = {}
    
    # Split by spaces and identify option codes
    parts = options_text.split()
    current_code = None
    current_value = []
    
    for part in parts:
        if len(part) == 2 and part.endswith('.') and part[0].isupper():
            # This is an option code like "A."
            if current_code and current_value:
                options[current_code] = ' '.join(current_value).strip()
            current_code = part[0]
            current_value = []
        else:
            if current_code:
                current_value.append(part)
    
    # Don't forget the last option
    if current_code and current_value:
        options[current_code] = ' '.join(current_value).strip()
    
    print(f"Parsed options: {options}")
    print(f"Code A decodes to: {options.get('A', 'A')}")
else:
    print("No MCQ found")