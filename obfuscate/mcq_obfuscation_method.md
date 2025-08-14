# MCQ Column Obfuscation Implementation

## Method: Distribution-Preserving Random Relabeling

### Overview
This obfuscation method maintains the overall distribution of MCQ (Multiple Choice Question) responses while introducing controlled noise to protect individual responses.

### Mathematical Foundation
Given MCQ categories with proportions **p** (e.g., Option A: 0.50, Option B: 0.30, Option C: 0.20):
- Each record is flipped with probability **α** (set to 0.10)
- If flipped: Draw a new category according to the original distribution **p**
- If not flipped (probability 1-α): Keep the original value
- Expected proportion after relabeling remains **p** (distribution invariant)

### Implementation Details

#### Algorithm Steps
1. **Calculate Original Distribution**: Count frequency of each option to get proportions
2. **Random Sampling**: For each record:
   - Generate random number r ∈ [0,1]
   - If r < α: Sample new value from original distribution
   - Otherwise: Keep original value
3. **Verification**: Confirm overall distribution remains approximately unchanged

#### Python Implementation
```python
def obfuscate_mcq_column(values, alpha=0.10):
    # Get original distribution
    distribution, categories = get_distribution(values)
    
    # Convert to cumulative for sampling
    cumulative = []
    cumsum = 0
    for cat in categories:
        cumsum += distribution[cat]
        cumulative.append((cumsum, cat))
    
    # Obfuscate values
    obfuscated = []
    for value in values:
        if random.random() < alpha:
            # Flip: draw from original distribution
            rand = random.random()
            for cum_prob, category in cumulative:
                if rand <= cum_prob:
                    obfuscated.append(category)
                    break
        else:
            # Keep original
            obfuscated.append(value)
    
    return obfuscated
```

### Applied Datasets

#### 1. Healthcare Dataset
**MCQ Columns**: Gender, Blood Type, Medical Condition, Insurance Provider, Admission Type, Medication, Test Results
- **Total records**: 150
- **Values changed**: 69 (approximately 10% per column)
- **Distribution preserved**: Verified post-obfuscation

#### 2. Stack Overflow Survey Dataset  
**MCQ Columns**: MainBranch, EdLevel, CompFreq
- **Total records**: 500
- **Values changed**: 50 (approximately 10% per column)
- **Distribution preserved**: Verified post-obfuscation

#### 3. SUS-UTA7 Dataset
**MCQ Columns**: group
- **Total records**: 90
- **Values changed**: 8 (approximately 10%)
- **Distribution preserved**: Verified post-obfuscation

### Key Properties

1. **Privacy Protection**: Individual responses are obfuscated with 10% probability
2. **Statistical Validity**: Overall distribution remains unchanged (invariant)
3. **Reversibility**: Not reversible without original data
4. **Reproducibility**: Uses fixed random seed (42) for consistent results

### Verification Results

Post-obfuscation distribution samples:
- **Healthcare Gender**: A: 46%, B: 53.3% (minimal change from original)
- **Healthcare Blood Type**: Maintains 8 categories with similar proportions
- **Stack Overflow MainBranch**: A: 94.4%, B: 5.6% (preserved)
- **Stack Overflow CompFreq**: A: 1.8%, B: 34.6%, C: 63.6% (preserved)

### Advantages
- Maintains aggregate statistics for analysis
- Simple to implement and understand
- Provides plausible deniability for individual responses
- No need for external noise parameters or complex transformations

### Limitations
- Not suitable for highly sensitive data requiring stronger privacy guarantees
- Fixed α value may not be optimal for all column types
- Assumes categorical independence (no cross-column relationships)