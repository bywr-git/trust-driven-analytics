# Acceptance Tests

The MVP is not complete until the following scenarios are tested.

## A. Upload and profiling
- [ ] A valid CSV can be uploaded.
- [ ] Column names, types, row count, and missing values are displayed.
- [ ] An empty or malformed CSV produces a clear error.
- [ ] The original uploaded data remains unchanged.

## B. Transformations
- [ ] A proposed transformation can be previewed before approval.
- [ ] Before-and-after values and row counts are visible.
- [ ] Every approved transformation has a history entry.
- [ ] Rejected rows can be inspected where applicable.
- [ ] The transformed dataset can be traced to its source version.

## C. Data model
- [ ] Tables, columns, and data types are inspectable.
- [ ] Candidate keys and relationships are labelled appropriately.
- [ ] A join that multiplies rows unexpectedly is flagged.
- [ ] Suggested relationships are not presented as confirmed facts.

## D. Requirements and dashboard
- [ ] A supported business requirement can be represented explicitly.
- [ ] The dashboard contains the requested metric and visualization.
- [ ] Users can edit supported chart properties.
- [ ] Unsupported or ambiguous requests are disclosed.

## E. Verification
- [ ] A correct metric passes an independent calculation check.
- [ ] A deliberately incorrect metric fails the check.
- [ ] Missing evidence cannot produce VERIFIED.
- [ ] Requirement coverage is reported separately from calculation accuracy.
- [ ] An edit invalidates and re-runs affected checks.
- [ ] Every result has an inspectable explanation and evidence record.

## F. Reporting and reproducibility
- [ ] The report identifies the dataset version used.
- [ ] Failed and inconclusive checks remain visible.
- [ ] Verification results can be reproduced from recorded inputs and rules.
- [ ] A clean test run passes in the project environment.

## G. Evaluation
- [ ] A benchmark contains known-correct and deliberately faulty cases.
- [ ] Defect detection recall and false-positive rate are measured.
- [ ] Critical-error escape rate is measured.
- [ ] Baseline and verified workflows are compared fairly.
