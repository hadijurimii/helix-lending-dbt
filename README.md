# Helix Lending Data Pipeline

This project builds a local data engineering pipeline for the Helix Lending take-home assessment. It ingests raw loan and payment sources, loads cleaned typed tables, and transforms them into queryable marts in DuckDB and Parquet.

## Project Summary

The source data contains loan originations in CSV and payment events in newline-delimited JSON. The messy parts are real enough to matter: duplicate IDs, mixed casing, mixed date formats, dollar-formatted amounts, malformed embedded JSON, missing payment amounts, optional metadata, and payment records that reference loans not present in the loan file.

The implemented pipeline keeps the shape simple:

- `raw`: source-faithful landing tables for auditability.
- `core`: cleaned and typed tables with normalized categories, parsed dates/timestamps, flattened JSON fields, and duplicate IDs removed by first-seen row.
- `marts`: modeled outputs for analysis: `dim_loans`, `fact_payments`, and `loan_payment_summary`.

DuckDB is the storage and transformation engine. It is the right size for this assessment: fast local SQL, native Parquet export, no pretend distributed stack.

## How To Run

```powershell
python main.py
```

Run tests:

```powershell
pytest -q
```

Run with Docker:

```powershell
docker compose up --build helix-pipeline
```

Run the optional dbt layer after generating the DuckDB database:

```powershell
python main.py
dbt run --profiles-dir . --project-dir .
dbt test --profiles-dir . --project-dir .
```

The pipeline writes:

- `output/helix_lending.duckdb`
- `output/parquet/raw_loans.parquet`
- `output/parquet/raw_payments.parquet`
- `output/parquet/core_loans_clean.parquet`
- `output/parquet/core_payments_clean.parquet`
- `output/parquet/dim_loans.parquet`
- `output/parquet/fact_payments.parquet`
- `output/parquet/loan_payment_summary.parquet`
- `output/metrics/run_metrics.json`
- `output/metrics/data_quality_report.json`

## Pipeline Stages

### Ingest

`data/loans.csv` and `data/payments.jsonl` are landed into `raw.loans_raw` and `raw.payments_raw`. The raw tables preserve source fields and add ingestion metadata.

Payment JSON is read with an explicit schema. DuckDB's auto inference was too clever with mixed timestamp formats, which is exactly how production bugs dress nicely for the interview.

### Load

The load stage creates `core.loans_clean` and `core.payments_clean`.

Loan cleanup:

- normalizes product, channel, and status casing
- parses principal amounts including commas and `$`
- parses origination dates from `%Y-%m-%d`, `%d-%b-%Y`, and `%m/%d/%Y`
- extracts borrower attributes from embedded JSON when valid
- keeps malformed borrower JSON as null parsed fields with `borrower_info_valid = false`
- deduplicates by `loan_id`, keeping the first source row

Payment cleanup:

- parses timestamps into UTC-naive timestamps for consistent querying
- preserves the original timestamp string
- flattens payment method and metadata JSON
- deduplicates by `payment_id`, keeping the first source row

### Transform

The transform stage publishes:

- `marts.dim_loans`: one row per loan with borrower attributes.
- `marts.fact_payments`: one row per payment with a `loan_exists` referential integrity flag.
- `marts.loan_payment_summary`: loan-level payment counts, total paid amount, first/last payment timestamps, and invalid payment amount counts.

## Data Quality

The pipeline writes `output/metrics/data_quality_report.json` with checks for:

- freshness: latest raw ingestion timestamps and latest source event dates
- completeness: missing customer IDs, malformed borrower JSON, missing payment amounts, missing metadata
- uniqueness: duplicate loan and payment IDs removed
- referential integrity: payments without matching loans

Latest full run observed:

- raw loans: `10,030`
- raw payments: `74,786`
- clean loans: `10,000`
- clean payments: `74,756`
- duplicate loans removed: `30`
- duplicate payments removed: `30`
- malformed borrower JSON rows: `30`
- missing customer IDs: `10`
- missing payment amounts: `75`
- payments without matching loans: `100`
- payments missing metadata: `7,405`

## Observability

The pipeline emits structured JSON logs to stdout for each stage and writes run metrics to `output/metrics/run_metrics.json`. Metrics include rows in, rows out, duration, database path, and quality report path.

Basic lineage:

- `data/loans.csv` -> `raw.loans_raw` -> `core.loans_clean` -> `marts.dim_loans` and `marts.loan_payment_summary`
- `data/payments.jsonl` -> `raw.payments_raw` -> `core.payments_clean` -> `marts.fact_payments` and `marts.loan_payment_summary`

## Tests

Tests cover date/timestamp parser behavior and one end-to-end fixture that verifies deduplication, amount parsing, JSON flattening, and orphan-payment flagging.

## Repository Structure

- `data/`: source files and data dictionary.
- `docs/`: architecture, lineage, operations, and interview debrief notes.
- `infographics/`: Mermaid visuals for architecture and quality findings.
- `models/`: optional dbt staging and mart models over the DuckDB output.
- `notebooklm/`: NotebookLM notes and presentation deck.
- `output/`: generated DuckDB, Parquet, metrics, and quality artifacts.
- `reports/`: human-readable quality and modeling summaries.
- `scripts/`: helper commands for pipeline, tests, dbt, and DuckDB inspection.
- `src/`: Python pipeline implementation.
- `tests/`: unit and end-to-end tests.

## Dependencies

- Python: implementation language requested by the assessment.
- DuckDB: local analytical database, SQL transform engine, and Parquet writer.
- pytest: small test runner for parser and end-to-end coverage.
- dbt-duckdb: optional analytics modeling layer over the generated DuckDB database.

## Known Limitations

- Duplicate conflict handling is first-seen-wins. That is acceptable for exact duplicate source rows, but real conflicting duplicates should be quarantined and reviewed.
- Naive payment timestamps are treated as already canonical. In production, I would require a source timezone contract.
- Referential failures are flagged, not dropped. Dropping them would hide a source system issue.
- The mart is intentionally small. It supports the assessment questions, but not a full lending warehouse.

## With More Time

- Add a quarantine table for invalid records and conflicting duplicates.
- Add Great Expectations or Soda only if the quality rules grow beyond a few SQL checks.
- Add incremental loading keyed by source file and event timestamp.
- Add a delinquency-specific mart once business rules define expected payment schedules and grace periods.
