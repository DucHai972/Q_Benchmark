Easy Mode
Logic: Find respondents who share a single, direct feature with a specific, named respondent. This involves a simple two-step "find-then-match" process.

Format Examples:
Which respondents were born in the same year as respondent '[ID]'?

Find all respondents with the same 'Socio-economic status' as respondent '[ID]', excluding the respondent themselves.

List all respondents who are the same gender as respondent '[ID]'.

Concrete Example:
Which respondents were born in the same year as respondent '113', excluding the respondent themselves?

Medium Mode
Logic: Find respondents who share a feature with a specific person and also meet another, independent condition. This adds a filtering step to the basic hop.

Format Examples:
Which respondents are the same gender as respondent '[ID]' and also have a 'Life satisfaction' score greater than [Number]?

Find all respondents whose mother has the same years of education as the mother of respondent '[ID]', and who also report a 'Stress' score of less than [Number].

List all respondents who were born in the same year as respondent '[ID]' and have a 'Happiness' score of [Number] or more.

Concrete Example:
Which respondents were born in the same year as respondent '113' and have a 'Worry' score of 3 or more?

Really Hard Mode
Logic: Find respondents who meet a condition that is relative to a calculated aggregate (like an average) from a different subgroup. This requires calculating a benchmark value first before finding the final group.

Format Examples:
Find all respondents whose '[Score Type]' is higher than the average '[Score Type]' for all respondents born in the same year as them.

Which respondents have more years of mother's education than the average father's education for all respondents with the same 'Socio-economic status'?

List all respondents whose total score for 'Anxiety Symptoms' is lower than the average total 'Depressive Symptoms' score for all respondents of the same gender.

Concrete Example:
Find all respondents whose 'Happiness' score is lower than the average 'Happiness' score for all respondents born in the same year as them.