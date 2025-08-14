Easy Mode
Logic: Applies a simple numerical rule to one or two fields. The rule usually involves a direct comparison (>, <, =) or a simple range.

Format Examples:
Which respondents have a [Numerical Field] greater than [Number]?

Find all respondents whose [Numerical Field] is between [Number A] and [Number B].

List all [Categorical Value] respondents whose [Numerical Field] is less than [Number].

Concrete Example:
Which respondents have a 'Billing Amount' between $15,000 and $45,000?

Medium Mode
Logic: Applies a rule to a calculated field (like length of stay) or combines multiple numerical and categorical rules to create a more specific filter.

Format Examples:
Find all respondents whose calculated length of stay is greater than [Number] days.

Which [Categorical Value] respondents are over the age of [Number] and have a [Numerical Field] less than [Number]?

List all respondents whose [Numerical Field] is an even number and who were admitted for an '[Admission Type]' procedure.

Concrete Example:
Which female patients have a 'Billing Amount' greater than $15,000 and are under the age of 50?

Really Hard Mode
Logic: Applies a rule that requires comparing an individual's value to a pre-calculated group aggregate (like an average or median). The rule is relative to a property of the group, not a fixed value.

Format Examples:
Find all respondents whose [Numerical Field] is greater than the average [Numerical Field] for their [Grouping Field].

Which respondents have a calculated length of stay that is more than double the average length of stay for their [Admission Type]?

List all respondents whose [Numerical Field] is within [Percentage]% of the [Superlative: e.g., highest] [Numerical Field] in their [Grouping Field].

Concrete Example:
Which patients have a 'Billing Amount' that is higher than the average billing amount for all patients with the same medical condition?