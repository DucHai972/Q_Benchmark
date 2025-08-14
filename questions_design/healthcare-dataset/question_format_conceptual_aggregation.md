Easy Mode
Logic: The count is based on one or two simple, direct filters on common fields.

Format Examples:
How many respondents have a [Categorical Field] of '[Value]'?

Count the respondents whose [Numerical Field] is greater than [Number].

How many respondents have [Field A] = '[Value A]' and [Field B] = '[Value B]'?

Concrete Example:
How many patients are male?

Medium Mode
Logic: The count is based on a combination of three or more filters, which can include simple calculations (like length of stay) or negative conditions.

Format Examples:
How many respondents with [Field A] = '[Value A]' and [Field B] = '[Value B]' have a [Numerical Field] below [Number]?

Count the respondents whose length of stay is between [Number A] and [Number B] days and who were admitted for an '[Admission Type]' procedure.

How many respondents from '[Hospital]' are over the age of [Number] and are not taking '[Medication]'?

Concrete Example:
How many male patients were admitted for an 'Emergency' and have a billing amount over $20,000?

Really Hard Mode
Logic: The count is based on criteria that first require an aggregate calculation (like an average) on a subgroup of the data. The filter itself is based on a derived value.

Format Examples:
How many respondents have a [Numerical Field] that is higher than the average [Numerical Field] for their [Grouping Field]?

Count the respondents who are in a hospital where the number of patients with [Condition A] is greater than the number of patients with [Condition B].

How many respondents over the age of [Number] have a length of stay that is longer than the average for their specific [Admission Type]?

Concrete Example:
How many patients have a billing amount that is higher than the average for their admission type?