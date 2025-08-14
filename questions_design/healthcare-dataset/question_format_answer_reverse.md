Easy Mode
Logic: The criteria involve one or two simple, direct filters on common fields, which may result in multiple respondents.

Format Examples:
Which respondents have a [Categorical Field] of '[Value]'?

Find all respondents whose [Numerical Field] is between [Number A] and [Number B].

List all respondents with [Field A] = '[Value A]' and [Field B] = '[Value B]'.

Concrete Example:
Which respondents have a blood type of 'O+'?

Medium Mode
Logic: The criteria involve a combination of three or more filters, which can include simple calculations (like length of stay) or negative conditions.

Format Examples:
Find all respondents with [Field A] = '[Value A]', [Field B] = '[Value B]', and whose [Numerical Field] is less than [Number].

Which respondents have a calculated length of stay greater than [Number] days and do not have a [Medical Condition] of '[Value]'?

List all respondents who are treated by the same doctor as the patient in room '[Room Number]' and were admitted for the same [Admission Type].

Concrete Example:
Which female respondents have 'Abnormal' test results and a billing amount less than $25,000?

Really Hard Mode
Logic: The criteria require an aggregate calculation (like an average) on a subgroup of the data to define the filter. This means the system must first analyze a group to derive a value before it can find the final list of respondents.

Format Examples:
Find all respondents from '[Hospital]' whose [Numerical Field] is greater than the average [Numerical Field] for all patients at that same hospital.

Which respondents are treated by a doctor who manages more patients with [Condition A] than [Condition B]?

List all respondents whose length of stay is longer than the average for their [Admission Type] and are over the age of [Number].

Concrete Example:
Find all respondents whose billing amount is higher than the average billing amount for all patients with the same insurance provider.