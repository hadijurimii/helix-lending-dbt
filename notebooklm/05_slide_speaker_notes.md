# Slide Speaker Notes

## Slide 1: A messy-data pipeline, not a big-data costume

Purpose: frame the project with taste and confidence.

Talk track:

- Two files, realistic mess.
- Python plus DuckDB.
- Raw to core to marts.
- Outputs are queryable and auditable.

## Slide 2: The source data fails in ways analysts actually feel

Purpose: show you understand the problem before showing the solution.

Talk track:

- Duplicate IDs create double counting risk.
- Mixed dates and timestamps break consistent time analysis.
- Malformed JSON breaks extraction.
- Orphan payments break joins.

## Slide 3: The architecture separates evidence, cleanup, and answers

Purpose: explain raw/core/marts visually.

Talk track:

- Raw: evidence.
- Core: standardization.
- Marts: analysis.
- Metrics and quality report wrap the run.

## Slide 4: Ingest is intentionally boring

Purpose: defend explicit schema and delayed parsing.

Talk track:

- Raw ingest should not be clever.
- Loan CSV read as strings.
- Payment JSON explicit schema.
- Timestamp parsing happens later.

## Slide 5: Load is where source chaos becomes typed data

Purpose: show practical cleaning decisions.

Talk track:

- Normalize casing.
- Strip `$` and commas from principal.
- Parse three date formats.
- Validate borrower JSON before extraction.

## Slide 6: The marts answer questions without hiding bad records

Purpose: show modeled outputs.

Talk track:

- `dim_loans` for loan attributes.
- `fact_payments` for events.
- `loan_payment_summary` for quick loan-level analysis.
- `loan_exists` protects referential visibility.

## Slide 7: Quality checks are visible and specific

Purpose: prove the pipeline actually measured source health.

Talk track:

- Freshness, completeness, uniqueness, referential integrity.
- Mention the exact counts.
- Emphasize flagged, not erased.

## Slide 8: Tests caught a real design issue

Purpose: show engineering maturity.

Talk track:

- Parser unit tests.
- End-to-end fixture.
- DuckDB JSON auto inference issue.
- Explicit schema became a tested design choice.

## Slide 9: Tradeoffs were deliberate

Purpose: preempt "why not Airflow/dbt/Spark?"

Talk track:

- This is not a scale problem.
- DuckDB keeps the surface area small.
- dbt is a natural next step.
- Quarantine and incremental loading are the next production improvements.

## Slide 10: Final takeaway

Purpose: close with a crisp thesis.

Talk track:

- Raw preserves evidence.
- Core standardizes truth.
- Marts answer questions.
- Quality reporting makes issues discussable.
