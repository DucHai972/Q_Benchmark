Easy Mode
Logic: Find respondents who share a single, direct feature with a specific, named respondent. This involves a simple two-step "find-then-match" process.

Format Examples:
Which respondents are in the same group as respondent '[ID]'?

Find all respondents who gave the same 'Ease_of_Use' score as respondent '[ID]', excluding the respondent themselves.

List all respondents who rated 'System_Complexity' the same as respondent '[ID]'.

Concrete Example:
Which respondents are in the same group as respondent '73', excluding the respondent themselves?

Medium Mode
Logic: Find respondents who share a feature with a specific person and also meet another, independent condition. This adds a filtering step to the basic hop.

Format Examples:
Which respondents are in the same group as respondent '[ID]' and also rated 'System_Complexity' as [Number]?

Find all respondents who gave the same 'Confidence_in_Use' score as respondent '[ID]' and who also strongly agree that the system is easy to learn (score of 5).

List all respondents who share the same 'Frequent_Usage' score as respondent '[ID]' but are not in the same group.

Concrete Example:
Find all respondents who gave the same 'Ease_of_Use' score as respondent '18' and are also in the 'Middle' group.

Really Hard Mode
Logic: Find respondents who meet a condition that is relative to a calculated aggregate (like an average) from a different subgroup. This requires calculating a benchmark value first before finding the final group.

Format Examples:
Find all respondents whose '[Score_Type]' is higher than the average '[Score_Type]' for a different group, such as the 'Senior' group.

Which respondents are in a group where the average 'System_Complexity' score is higher than the average 'Ease_of_Use' score for that same group?

List all respondents whose total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') is lower than the average for all respondents in a different group.

Concrete Example:
Find all respondents whose 'Frequent_Usage' score is lower than the average 'Frequent_Usage' score for the 'Middle' group.