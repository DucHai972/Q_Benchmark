# Data Obfuscation Method: Rank Swapping

## Overview

This document describes the rank swapping method used to obfuscate numeric data while preserving statistical properties and relationships in the Q_Benchmark datasets.

## Method Description

### Rank Swapping Algorithm

For each numeric variable X in the dataset:

1. **Ranking Phase**: Sort all values of X by their numeric value and assign ranks (1 to n)
2. **Swap Partner Selection**: For each record at rank r, randomly select a swap partner from the window [r-w, r+w]
3. **Value Swapping**: Exchange the values between the original record and its selected swap partner
4. **Window Size**: w ≈ 2.5% of n (total number of records)

### Example Implementation

Consider the Age column in a healthcare dataset:

```
Original Data:
Respondent | Age
1          | 25
2          | 45  
3          | 30
4          | 22
5          | 50

Step 1: Sort by Age and assign ranks
Rank | Respondent | Age
1    | 4          | 22
2    | 1          | 25  
3    | 3          | 30
4    | 2          | 45
5    | 5          | 50

Step 2: For each rank, select swap partner within window
- Window size w = ceil(0.025 * 5) = 1
- Rank 1 (value 22): can swap with ranks [1,2] → randomly select rank 2
- Rank 2 (value 25): can swap with ranks [1,3] → randomly select rank 1
- Rank 3 (value 30): can swap with ranks [2,4] → randomly select rank 4
- Rank 4 (value 45): can swap with ranks [3,5] → randomly select rank 3
- Rank 5 (value 50): can swap with ranks [4,5] → randomly select rank 5 (no swap)

Step 3: Perform swaps
- Swap rank 1 ↔ rank 2: 22 ↔ 25
- Swap rank 3 ↔ rank 4: 30 ↔ 45
- Rank 5: no change

Final Result:
Respondent | Age (obfuscated)
1          | 22  (was 25)
2          | 30  (was 45)
3          | 45  (was 30)  
4          | 25  (was 22)
5          | 50  (unchanged)
```

## Key Properties Preserved

1. **Distribution Shape**: The overall distribution of values remains unchanged
2. **Range**: Min and max values are preserved
3. **Statistical Moments**: Mean, variance, and higher moments are maintained
4. **Rank Correlation**: Correlations between variables are approximately preserved due to local swapping

## Implementation Details

### Window Size Calculation
- w = max(1, ceil(0.025 * n)) where n is the number of records
- Ensures at least one potential swap partner even for small datasets
- 2.5% provides good balance between privacy protection and utility preservation

### Handling Edge Cases
- **Boundary Ranks**: Ranks near 1 or n have asymmetric windows
- **Duplicate Values**: Records with identical values can be swapped freely
- **Missing Values**: Excluded from ranking and swapping process
- **Date Columns**: Treated as numeric by converting to days since epoch

### Random Seed
- Uses fixed random seed for reproducible results
- Seed can be varied to generate different obfuscation patterns

## Privacy Benefits

1. **Individual Record Protection**: No individual retains their exact original values
2. **Relationship Obfuscation**: Direct value-to-respondent mapping is broken
3. **Query Resistance**: Range queries return different sets of respondents
4. **Linkage Prevention**: Reduces risk of linking with external datasets

## Utility Preservation

1. **Statistical Analysis**: Aggregate statistics remain valid
2. **Machine Learning**: Model performance is largely maintained
3. **Correlation Analysis**: Relationship patterns are preserved
4. **Distribution Analysis**: Histograms and density plots remain similar

## File Naming Convention

Obfuscated files follow the pattern: `{original_name}.obfuscated.csv`

Examples:
- `healthcare_questionnaire.numeric.csv` → `healthcare_questionnaire.numeric.obfuscated.csv`
- `sus_uta7_questionnaire.numeric.csv` → `sus_uta7_questionnaire.numeric.obfuscated.csv`