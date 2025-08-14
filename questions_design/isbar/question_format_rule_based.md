Easy Mode
Logic: Applies a simple numerical rule to one or two fields. The rule usually involves a direct comparison (>, <, =) or a simple range.

Format Examples:
Which respondents scored higher than [Number] on '[Score Type]'?

Find all respondents whose '[Score Type]' score is between [Number A] and [Number B].

List all respondents from the '[Session Name]' session whose '[Score Type]' is exactly [Number].

Concrete Example:
Which respondents scored 3 on 'Identification'?

Medium Mode
Logic: Applies a rule to a calculated field (like a total score) or combines multiple numerical and categorical rules to create a more specific filter.

Format Examples:
Find all respondents whose total score for '[Score A]' and '[Score B]' is greater than [Number].

Which respondents from sessions on '[Date]' have a '[Score A]' of [Number] and a '[Score B]' of less than [Number]?

List all respondents whose '[Score A]' score is equal to their '[Score B]' score.

Concrete Example:
Find all respondents whose 'Assessment' score is equal to their 'Background (examination)' score.

Really Hard Mode
Logic: Applies a rule that requires comparing an individual's value to a pre-calculated group aggregate (like an average or median). The rule is relative to a property of the group, not a fixed value.

Format Examples:
Find all respondents whose '[Score Type]' is greater than the average '[Score Type]' for their [Grouping Field: e.g., Session Name].

Which respondents have a total score across all items that is lower than the average total score for all sessions on the same date?

List all respondents whose '[Score A]' is within [Number] point of the lowest '[Score B]' for their [Grouping Field].

Concrete Example:
Which respondents have a total score across all rubric items that is higher than the average total score for all respondents?