Easy Mode
Logic: This is the most straightforward mode. It involves counting respondents based on one or two simple, direct filters. It answers the question "Count the respondents with property X."

Format Examples:
Count the respondents with a [Categorical Field] of '[Value]'.

Count the respondents whose [Numerical Field] is greater than [Number].

Count the respondents with [Field A] = '[Value A]' and [Field B] = '[Value B]'.

Concrete Example (using the developer survey dataset):
Count the respondents who have worked with the 'Python' language.

Medium Mode
Logic: This mode increases complexity by combining three or more conditions. It can also involve filters based on simple calculations derived from an individual respondent's own data (e.g., a total score or a date duration).

Format Examples:
Count the respondents with [Field A] = '[Value A]' and [Field B] = '[Value B]' who have a [Numerical Field] below [Number].

Count the respondents whose calculated [Derived Field: e.g., length of stay] is between [Number A] and [Number B] and who meet '[Condition A]'.

Count the respondents from '[Group]' with a total score across '[Score A]' and '[Score B]' that is greater than [Number].

Concrete Example (using the developer survey dataset):
Count the respondents who are 'Employed, full-time' and have worked with both 'Docker' and 'npm'.

Really Hard Mode
Logic: This is the most advanced mode. It involves counting respondents based on a comparison to a group-level aggregate. The system must first calculate a benchmark (like an average or median for a specific subgroup) and then use that benchmark to filter and count the final set of respondents.

Format Examples:
Count the respondents with a [Numerical Field] that is higher than the average [Numerical Field] for their [Grouping Field].

Count the respondents who are in a group where the number of individuals with [Condition A] is greater than the number with [Condition B].

Count the respondents with [Condition A] who have a [Numerical Field] that is lower than the overall average for all respondents.

Concrete Example (using the developer survey dataset):
Count the respondents with more years of professional coding experience than the average for all respondents with the same education level.