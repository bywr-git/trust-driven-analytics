# Product Specification

## Problem
AI-assisted analytics can produce convincing dashboards with incorrect
calculations, misunderstood business requirements, or undocumented data
transformations.

## Product goal
Build an analytics application that generates editable dashboards and
independently checks their data, calculations, and requirement coverage.

## Primary user
A business analyst or small-business owner working with tabular data.

## Initial use case
Retail sales analysis using an uploaded CSV.

## User workflow
1. Upload a CSV file.
2. Inspect columns, data types, missing values, and possible issues.
3. Inspect the proposed data model and relationships.
4. Preview and approve or reject proposed transformations.
5. Enter business requirements in structured or natural language.
6. Generate an interactive dashboard.
7. Independently verify calculations and requirement coverage.
8. Inspect evidence and unresolved issues.
9. Edit the dashboard and re-run affected checks.
10. Export the report and, where appropriate, the transformed dataset.

## Core modules
- Data ingestion and profiling
- Data transformation explorer
- Data model and lineage explorer
- Requirement representation
- Dashboard generation and editing
- Independent verification engine
- Evidence and trust report
- Evaluation and test harness

## Verification outcomes
- VERIFIED: the defined check passed.
- FAILED: the check found a demonstrated defect.
- INCONCLUSIVE: available evidence is insufficient.
- HUMAN_REVIEW_NEEDED: a decision requires user confirmation.

These are check outcomes, not a single overall trust score.

## Design principles
- Never silently modify or discard source records.
- Preserve transformation history and source-to-output lineage.
- Distinguish observed facts from inferred relationships.
- Keep verification independent from dashboard-generation logic.
- Use deterministic calculations for critical checks.
- Require confirmation for ambiguous or consequential transformations.
- Re-verify affected checks after relevant edits.
- Do not claim that an untested result is verified.

## Initial technology
Python, Pandas, DuckDB, Streamlit, Plotly, Pydantic, and pytest.

## Out of scope for the first MVP
- Training a foundation model
- Autonomous changes to external business systems
- Multi-user enterprise infrastructure
- Arbitrary execution of generated code
- Unverified automatic deletion or correction of data
- Paid APIs as a mandatory dependency
