### Easy Mode
Logic: The respondent is identified using one or two direct and explicit pieces of information. This requires no complex calculations.

Format Examples:
What is the [Feature] of the respondent '[ID]'?

What is the [Feature] of the [Superlative: e.g., oldest, youngest] respondent?

What is the [Feature] of the respondent with [Field A] = '[Value A]' and [Field B] = '[Value B]'?

Concrete Example:
What is the room number of the patient in room 305 at 'County General' hospital?

### Medium Mode
Logic: The respondent is identified by combining three or more criteria. This may involve finding a superlative within a specific group or using a simple calculation.

Format Examples:
What is the [Feature] of the [Superlative] respondent with [Field A] = '[Value A]' and [Field B] = '[Value B]'?

What is the [Feature] of the respondent with the [Superlative] [Numerical Field] among those with [Field A] = '[Value A]'?

What is the [Feature] of the respondent whose [Calculated Field: e.g., length of stay] is greater than [Number] and has [Field A] = '[Value A]'?

Concrete Example:
What is the primary medication prescribed to the patient with 'Cigna' insurance who has the highest billing amount?

### Really Hard Mode
Logic: Identifying the respondent requires an initial calculation or aggregation on a subgroup of the data. The filter itself is based on a derived value.

Format Examples:
What is the [Feature] of the respondent whose [Numerical Field] is the [Superlative] above the [Aggregate: e.g., average] for all respondents with the same [Grouping Field]?

What is the [Feature] of the [Superlative Adjective: e.g., oldest] respondent who meets a calculated condition ([Calculated Field] > [Number]) and a categorical condition ([Field A] = '[Value A]')?

Concrete Example:
What is the age of the patient whose billing amount is the highest above the average bill for all patients with the same insurance provider?