# Verification Rules

## 1. Source integrity
- Record the uploaded filename and dataset version.
- Record row and column counts.
- Preserve the original dataset separately from transformed data.
- Record a content hash when practical.

## 2. Data quality
Check for:
- Missing values
- Invalid numeric values
- Duplicate records under explicitly defined rules
- Unexpected data types
- Invalid dates
- Suspicious values and inconsistent categories

A duplicate-looking row is not automatically an error.

## 3. Requirement coverage
Represent each requirement as a structured, testable item.

Example:
"Show monthly sales for the selected period."

Expected components:
- Metric: sales
- Aggregation: sum
- Time grouping: month
- Filter scope: selected period
- Expected visualization: time series

Flag ambiguous requirements rather than silently guessing.

## 4. Independent calculation checks
For supported metrics, calculate expected results independently
from the values used to render the dashboard.

Example:
- Expected total sales: independently calculated from source data.
- Displayed total sales: extracted from the dashboard's metric result.
- Check: compare both values using an explicit numeric tolerance.

Do not verify a result by simply asking the component that generated
it whether it is correct.

## 5. Transformation checks
For each transformation, record:
- Transformation ID
- Input dataset version
- Operation and parameters
- Reason
- Rows affected
- Output dataset version
- Validation result

Preserve rejected or quarantined rows when applicable.

## 6. Relationship and join checks
Before relying on a join, inspect:
- Candidate key uniqueness
- Unmatched records
- Row counts before and after the join
- Unexpected row multiplication
- Whether the relationship has been confirmed by the user

Inferred relationships must remain suggestions until validated.

## 7. Evidence records
Each verification result should identify:
- Check ID and rule version
- Check status
- Dataset version
- Requirement or metric being checked
- Expected result, where applicable
- Observed result, where applicable
- Evidence or reproducible calculation
- Explanation
- Timestamp

## 8. Failure handling
- Missing evidence must not produce VERIFIED.
- A failed critical check must be visible to the user.
- Unsupported calculations must be marked INCONCLUSIVE.
- Ambiguous business rules must be sent for HUMAN_REVIEW_NEEDED.
- Relevant dashboard or data changes must invalidate affected checks.

## 9. Evaluation
Measure:
- Defect detection recall
- False-positive rate
- Requirement coverage
- Critical-error escape rate
- Verification latency
- Human validation time

Do not invent a composite trust score without a justified definition
and empirical evaluation.
