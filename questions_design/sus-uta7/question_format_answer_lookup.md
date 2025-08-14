Easy Mode
Logic: The respondent is identified using one or two direct, explicit criteria like their ID, group, or a specific answer.

Format Examples:
What is the [Feature: e.g., 'Ease_of_Use' score] of respondent '[ID]'?

What is the [Feature: e.g., Group] of the respondent who rated '[Score_Type]' as [Number]?

Concrete Example:
What is the 'Group' of respondent '73'?

Medium Mode
Logic: The respondent is identified by combining three or more criteria. This often involves finding a superlative (e.g., highest or lowest score) within a specific group or performing a simple calculation on a respondent's own scores.

Format Examples:
What is the [Feature] of the respondent from the '[Group]' group with the highest [Score_Type] score?

What is the [Feature] of the respondent from the '[Group]' group who rated '[Score_A]' as [Number] and '[Score_B]' as [Number]?

What is the [Feature] of the respondent whose combined score for '[Score_A]' and '[Score_B]' was exactly [Number]?

Concrete Example:
What is the 'Frequent_Usage' score of the respondent from the 'Middle' group who rated 'System_Complexity' as 1 and 'Confidence_in_Use' as 5?

Really Hard Mode
Logic: Identifying the respondent requires an initial calculation or aggregation (like an average) on a subgroup of the data. The filter itself is based on a derived value that must be computed first.

Format Examples:
What is the [Feature] of the respondent from the '[Group_A]' group whose [Score_Type] is higher than the average [Score_Type] for the '[Group_B]' group?

What is the [Feature] of the respondent with the highest total positive score ('Ease_of_Use' + 'Integration_of_Functions') who is not in the '[Group]' group?

What is the [Feature] of the respondent whose score for '[Score_A]' is the same as the score for '[Score_B]' from the respondent with the lowest 'Frequent_Usage' score?

Concrete Example:
What is the 'Inconsistency' score of the respondent from the 'Middle' group whose 'Ease_of_Use' score is lower than the average 'Ease_of_Use' score for all Interns?