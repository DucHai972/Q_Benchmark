Easy Mode
Logic: Find respondents who share a single, direct feature with a specific, named respondent. This involves a simple two-step "find-then-match" process.

Format Examples:
Which respondents participated in the same session name as respondent '[ID]'?

Find all respondents who had a session on the same date as respondent '[ID]', excluding the respondent themselves.

List all respondents who scored the same on '[Score Type]' as respondent '[ID]'.

Concrete Example:
Which respondents scored the same on 'Identification' as respondent '19'?

Medium Mode
Logic: Find respondents who share a feature with a specific person and also meet another, independent condition. This adds a filtering step to the basic hop.

Format Examples:
Which respondents had a session on the same date as respondent '[ID]' and also scored [Number] on '[Score Type]'?

Find all respondents who participated in the same session name as respondent '[ID]' and whose comments contain the word '[keyword]'.

List all respondents who scored the same on '[Score A]' as respondent '[ID]' and also scored perfectly on '[Score B]'.

Concrete Example:
Find all respondents who scored the same on 'Situation' as respondent '19' and also have a 'Global Rating Scale' score of 2.

Really Hard Mode
Logic: Find respondents who meet a condition that is relative to a calculated aggregate (like an average) from a different subgroup. This requires calculating a benchmark value first before finding the final group.

Format Examples:
Find all respondents whose '[Score Type]' is higher than the average '[Score Type]' for all sessions that happened on the same date as respondent '[ID]'s session.

Which respondents are from a session name where the average '[Score_Type]' score is higher than the overall average for all sessions?

List all respondents whose total score across all rubric items is lower than the average total score for all sessions on a specific '[Date]'.

Concrete Example:
Find all respondents whose 'Background (history)' score is lower than the average 'Background (history)' score for all sessions that occurred on May 16th, 2025.