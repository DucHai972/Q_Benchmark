Easy Mode
Logic: The criteria involve one or two simple, direct filters on categorical, numerical, or list-based features.

Format Examples:
Which respondents are from '[Country]'?

Find all respondents with more than [Number] years of professional coding experience.

List all respondents who have worked with the '[Language]' language.

Concrete Example:
Which respondents have worked with the 'Rust' language?

Medium Mode
Logic: The criteria involve a combination of three or more filters, which can include calculations, negative conditions, or multiple list/text matching conditions.

Format Examples:
Find all respondents from '[Country]' with an education level of '[EdLevel]' who have worked with '[Language]'.

Which respondents have between [Number A] and [Number B] years of total coding experience and work with the '[Tool]' tool?

List all respondents whose yearly compensation is over [Amount] and who do not use '[VCS]' for version control.

Concrete Example:
Which respondents work in an organization of '100 to 499 employees', use 'Git', and have worked with 'TypeScript'?

Really Hard Mode
Logic: The criteria require an aggregate calculation (like an average) on a subgroup of the data to define the filter. This means the system must first analyze a group to derive a value before it can find the final list of respondents.

Format Examples:
Find all respondents whose total compensation is higher than the average compensation for their country.

Which respondents have more professional coding experience than the average for their education level?

List all respondents who have worked with a language that is also one of the top 3 most desired languages among all respondents in their same organization size.

Concrete Example:
Find all respondents whose total yearly compensation is higher than the average for their organization size.