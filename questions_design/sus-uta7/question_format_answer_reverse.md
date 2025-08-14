Easy Mode
Logic: The criteria involve one or two simple, direct filters on common fields, which may result in multiple respondents.

Format Examples:
Which respondents are in the '[Group]' group?

Find all respondents who rated '[Score_Type]' as [Number].

List all respondents from the '[Group]' who rated '[Score_Type]' as [Number].

Concrete Example:
Which respondents are in the 'Middle' group?

Medium Mode
Logic: The criteria involve a combination of three or more filters, which can include simple calculations on a respondent's own scores, negative conditions, or text matching.

Format Examples:
Which respondents from the '[Group]' group rated '[Score_A]' as [Number] and '[Score_B]' as [Number]?

Find all respondents whose combined score for '[Score_A]' and '[Score_B]' is less than [Number].

List all respondents who rated '[Score_A]' and '[Score_B]' with the same score.

Concrete Example:
Find all respondents from the 'Middle' group whose 'System_Complexity' score is 1.

Really Hard Mode
Logic: The criteria require an aggregate calculation (like an average) on a subgroup of the data to define the filter. This means the system must first analyze a group to derive a value before it can find the final list of respondents.

Format Examples:
Find all respondents in the '[Group_A]' group whose '[Score_Type]' is higher than the average '[Score_Type]' for the '[Group_B]' group.

Which respondents have a total negative usability score ('System_Complexity' + 'Inconsistency' + 'Cumbersome_to_Use') that is higher than the average for their group?

List all respondents whose score for '[Score_Type]' is below the average for all respondents who are not in their group.

Concrete Example:
Find all respondents whose 'Confidence_in_Use' score is higher than the average 'Confidence_in_Use' score for their group.