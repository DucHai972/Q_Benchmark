Easy Mode
Logic: Applies a simple numerical rule to one or two fields. The rule usually involves a direct comparison (>, <, =) or a simple range.

Format Examples:
Which respondents have a [Numerical Field] greater than [Number]?

Find all respondents whose [Numerical Field] is between [Number A] and [Number B].

List all respondents from '[Country]' whose [Numerical Field] is less than [Number].

Concrete Example:
Which respondents have more than 10 years of professional coding experience?

Medium Mode
Logic: Applies a rule to a calculated field (like normalized yearly compensation) or combines multiple numerical and categorical rules to create a more specific filter.

Format Examples:
Find all respondents whose calculated yearly compensation is greater than [Amount].

Which respondents from '[Country]' have more than [Number] 'YearsCode' and a yearly compensation less than [Amount]?

List all respondents for whom their professional coding years are less than half their total coding years.

Concrete Example:
Find all respondents whose professional coding years are less than half their total coding years.

Really Hard Mode
Logic: Applies a rule that requires comparing an individual's value to a pre-calculated group aggregate (like an average or median). The rule is relative to a property of the group, not a fixed value.

Format Examples:
Find all respondents whose [Numerical Field] is greater than the average [Numerical Field] for their [Grouping Field: e.g., Country].

Which respondents have a calculated yearly compensation that is more than double the average for their [EdLevel]?

List all respondents whose '[Numerical Field]' is within [Percentage]% of the [Superlative: e.g., highest] '[Numerical Field]' in their [Grouping Field].

Concrete Example:
Which respondents have a yearly compensation that is higher than the average yearly compensation for all respondents with the same education level?