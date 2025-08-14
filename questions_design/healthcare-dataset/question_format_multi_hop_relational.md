Easy Mode
Logic: Find respondents who share a single, direct feature with a specific, named respondent. This involves a simple two-step "find-then-match" process.

Format Examples:
Which respondents are in the same hospital as respondent '[ID]'?

Find all respondents with the same insurance provider as respondent '[ID]', excluding the respondent themselves.

List all respondents who are treated by the same doctor as respondent '[ID]'.

Concrete Example:
Which respondents have the same insurance provider as respondent '144'?

Medium Mode
Logic: Find respondents who share a feature with a specific person and also meet another, independent condition. This adds a filtering step to the basic hop.

Format Examples:
Which respondents are in the same hospital as respondent '[ID]' and also have a 'Billing Amount' over [Number]?

Find all respondents who are treated by the same doctor as respondent '[ID]' and who have 'Abnormal' test results.

List all respondents who have the same 'Admission Type' as respondent '[ID]' but are a different gender.

Concrete Example:
Which respondents have the same insurance provider as respondent '144' and also have 'Abnormal' test results?

Really Hard Mode
Logic: Find respondents who meet a condition that is relative to a calculated aggregate from a different subgroup or from a benchmark respondent. This requires calculating a benchmark value or finding a benchmark respondent first.

Format Examples:
Find all respondents whose billing amount is higher than the average for all patients treated by the same doctor as respondent '[ID]'.

Which respondents are from a hospital where the average age of patients is lower than the overall average age of all respondents?

List all respondents who are taking the same medication as the youngest patient with 'Cancer'.

Concrete Example:
Which patients have the same medical condition as the patient with the highest billing amount, and are also older than that patient?