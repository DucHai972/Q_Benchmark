Mode 1: Direct Aggregation (Easy)
Logic: This is the most straightforward mode. It involves counting respondents based on one or two simple, direct filters. It answers the question "Count the respondents with property X."

Format Examples:
Count the respondents who are in the '[Group]' group.

Count the respondents who rated '[Score_Type]' as [Number].

Count the respondents from the '[Group]' who rated '[Score_Type]' as [Number].

Concrete Example:
Count the respondents who are in the 'Middle' group.

Mode 2: Multi-Conditional Aggregation (Medium)
Logic: This mode increases complexity by combining three or more conditions. It can also involve filters based on simple calculations derived from an individual respondent's own data (e.g., a total score).

Format Examples:
Count the respondents from the '[Group]' group who rated '[Score_A]' as [Number] and '[Score_B]' as [Number].

Count the respondents whose combined score for '[Score_A]' and '[Score_B]' is less than [Number].

Count the respondents who rated '[Score_A]' and '[Score_B]' with the same score.

Concrete Example:
Count the respondents from the 'Middle' group who have a 'System_Complexity' score of 1.

Mode 3: Comparative Aggregation (Really Hard)
Logic: This is the most advanced mode. It involves counting respondents based on a comparison to a group-level aggregate. The system must first calculate a benchmark (like an average or median for a specific subgroup) and then use that benchmark to filter and count the final set of respondents.

Format Examples:
Count the respondents in the '[Group_A]' group who have a '[Score_Type]' score that is higher than the average '[Score_Type]' for the '[Group_B]' group.

Count the respondents who are in a group where the average 'System_Complexity' score is higher than the average 'Ease_of_Use' score.

Count the respondents who have a total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') that is lower than the average for all respondents not in their group.

Concrete Example:
Count the respondents who have a 'Confidence_in_Use' score that is higher than the average 'Confidence_in_Use' score for their group.