Easy Mode
Logic: Applies a simple numerical rule to one or two fields. The rule usually involves a direct comparison (>, <, =) or a simple range.

Format Examples:
Which respondents scored higher than [Number] on '[Score Type]'?

Find all respondents whose '[Score Type]' score is between [Number A] and [Number B].

List all respondents from the '[Group]' group whose '[Score Type]' is exactly [Number].

Concrete Example:
Which respondents from the 'Middle' group scored 5 on 'Need_for_Technical_Support'?

Medium Mode
Logic: Applies a rule to a calculated field (like a total score) or combines multiple numerical and categorical rules to create a more specific filter.

Format Examples:
Find all respondents whose total score for '[Score A]' and '[Score B]' is less than [Number].

Which respondents from the '[Group]' group have a '[Score A]' of [Number] or more and a '[Score B]' of less than [Number]?

List all respondents whose '[Score A]' score is greater than their '[Score B]' score.

Concrete Example:
Find all respondents whose 'Ease_of_Use' score is greater than their 'System_Complexity' score.

Really Hard Mode
Logic: Applies a rule that requires comparing an individual's value to a pre-calculated group aggregate (like an average or median). The rule is relative to a property of the group, not a fixed value.

Format Examples:
Find all respondents whose '[Score Type]' is greater than the average '[Score Type]' for their [Grouping Field: e.g., Group].

Which respondents have a total positive usability score ('Ease_of_Use' + 'Integration_of_Functions') that is lower than the average for all respondents in a different group?

List all respondents whose '[Score A]' is within [Number] point of the highest '[Score B]' for their [Grouping Field].

Concrete Example:
Which respondents have an 'Ease_of_Use' score that is higher than the average 'Ease_of_Use' score for their group?