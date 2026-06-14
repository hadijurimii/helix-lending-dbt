# Progress

## Completed

- Ingested raw loan CSV and payment JSONL into DuckDB.
- Loaded cleaned core tables with typed fields, normalized categories, parsed dates, parsed timestamps, and flattened JSON.
- Built mart outputs for loans, payments, and loan-level payment summaries.
- Added structured logging, run metrics, and a data quality report.
- Added parser unit tests and an end-to-end fixture test.
- Added NotebookLM study notes and an editable presentation deck.
- Added Docker, dbt project files, documentation, reports, scripts, and infographics.

## Current Data Quality Snapshot

- Raw loans: `10,030`
- Raw payments: `74,786`
- Clean loans: `10,000`
- Clean payments: `74,756`
- Duplicate loans removed: `30`
- Duplicate payments removed: `30`
- Malformed borrower JSON rows: `30`
- Missing payment amounts: `75`
- Orphan payments: `100`

## Next Best Improvements

- Add quarantine tables for invalid records and conflicting duplicates.
- Move production SQL ownership fully into dbt models.
- Add incremental source loading.
- Add a delinquency mart after business rules define schedules, due dates, and grace periods.
