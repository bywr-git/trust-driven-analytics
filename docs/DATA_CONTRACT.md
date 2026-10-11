# Data Contract

## Dataset version
Every source or transformed dataset must have a distinct version identifier.

Record:
- Dataset ID and version
- Source filename
- Row and column counts
- Column names and inferred data types
- Creation time
- Parent dataset version, if transformed

## Transformation record
Every transformation must record:
- Transformation ID
- Input and output dataset versions
- Operation name
- Parameters
- Reason or user instruction
- Number of affected rows
- Validation outcome

Transformations must be reproducible where practical.

## Data model
For each table or dataset, record:
- Table or dataset name
- Columns and data types
- Candidate keys
- Missing-value counts
- Potential relationships
- Whether each relationship is inferred or user-confirmed

## Metric definition
Each supported metric should record:
- Metric ID and display name
- Source columns
- Aggregation or formula
- Filters
- Grouping dimensions
- Units, if known
- Null-handling policy
- Calculation version

Example:
- Name: Total Sales
- Source: sales_amount
- Formula: sum(sales_amount)
- Null policy: explicitly defined and tested
- Output: numeric value in the source currency, if known

## Lineage
A derived metric must be traceable to:
source dataset version -> transformations -> source columns -> calculation
-> verification checks -> displayed result.

## Safety
Never overwrite the original uploaded dataset with cleaned data.
Never fabricate missing business values without explicit authorization.
Never describe an inferred relationship as confirmed.
