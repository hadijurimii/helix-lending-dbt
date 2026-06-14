# Helix Lending Pipeline: NotebookLM Source Pack

## One-Sentence Summary

This project builds a local Python and DuckDB data pipeline that ingests messy lending source files, cleans and models them into analytical marts, writes Parquet and DuckDB outputs, and exposes run metrics plus data quality checks.

## What The Assessment Asked For

Helix Lending provided two raw sources:

- `data/loans.csv`: loan origination records with duplicate loan IDs, inconsistent casing, mixed date formats, embedded borrower JSON, and occasional malformed values.
- `data/payments.jsonl`: payment events with nested JSON, missing fields, duplicate payment IDs, mixed timestamp formats, and some payments that do not match any known loan.

The deliverable needed a working pipeline, quality checks, observability, tests, a README, and an AI collaboration log.

## Implemented Architecture

The pipeline uses three data layers:

- `raw`: source-faithful landing tables. These preserve input fields plus ingestion metadata.
- `core`: cleaned and typed tables. These normalize categories, parse dates and timestamps, flatten JSON fields, and remove duplicate IDs.
- `marts`: query-ready analytical outputs for presentation and downstream analysis.

Main outputs:

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

## Why DuckDB

DuckDB is a strong fit because the data is local and modest in size: about 10k loan rows and 75k payment rows. It gives SQL transformations, fast local analytics, and native Parquet export without unnecessary orchestration or distributed compute.

The key defense: this project is not big data. It is messy data. The right answer is correctness, observability, and explainability.

## Pipeline Entry Points

Run the full pipeline:

```powershell
python main.py
```

Run tests:

```powershell
pytest -q
```

## Important Files

- `main.py`: thin CLI entrypoint.
- `src/helix_pipeline/pipeline.py`: ingest, load, transform, metrics, and quality report logic.
- `src/helix_pipeline/parsers.py`: reusable date and timestamp parsing helpers.
- `src/helix_pipeline/config.py`: path configuration.
- `src/helix_pipeline/logging_utils.py`: structured JSON logging.
- `tests/test_parsers.py`: unit tests for date and timestamp parsing.
- `tests/test_pipeline_e2e.py`: end-to-end fixture test.

## Ingest Stage

The ingest stage creates:

- `raw.loans_raw`
- `raw.payments_raw`

Loan CSV is read as varchar to avoid premature type failures.

Payment JSONL is read with an explicit schema. This was a deliberate fix. DuckDB's auto inference tried to infer timestamp types and failed on mixed `Z`, offset, and naive timestamp formats. The pipeline keeps timestamps as strings during ingest and parses them during load.

## Load Stage

The load stage creates:

- `core.loans_clean`
- `core.payments_clean`

Loan cleaning:

- trims and normalizes `product_type`, `origination_channel`, and `status`
- parses `principal_amount`, including commas and dollar signs
- casts interest rate and term months
- parses dates from `YYYY-MM-DD`, `DD-Mon-YYYY`, and `MM/DD/YYYY`
- validates and extracts borrower JSON fields
- keeps malformed borrower JSON auditable through `borrower_info_raw` and `borrower_info_valid`
- deduplicates by `loan_id`, keeping the first source row

Payment cleaning:

- deduplicates by `payment_id`, keeping the first source row
- parses timestamps into UTC-normalized timestamp fields
- preserves the raw timestamp
- flattens payment method fields
- flattens optional metadata fields

## Transform Stage

The transform stage creates:

- `marts.dim_loans`: one row per cleaned loan.
- `marts.fact_payments`: one row per cleaned payment, including `loan_exists`.
- `marts.loan_payment_summary`: loan-level payment count, total paid amount, first/last payment timestamps, and invalid payment amount count.

The design is a small star-style model rather than one big table. This keeps loan attributes and payment events separate while still giving a summary mart for quick analysis.

## Data Quality Results

Latest full run:

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

Quality categories covered:

- freshness: latest ingestion timestamp and latest source event dates
- completeness: missing customer IDs, malformed borrower JSON, missing payment amounts, missing metadata
- uniqueness: duplicate loan IDs and payment IDs removed
- referential integrity: payment rows without matching loans

## Observability

The pipeline emits structured JSON logs to stdout and writes `run_metrics.json`.

Each stage reports:

- start and finish
- rows in
- rows out
- duration
- output paths

## Design Decisions To Defend

Decision: Use DuckDB and Parquet.

Reason: Local analytical workload, small enough to avoid Spark/Airflow ceremony, but realistic enough to benefit from SQL and durable file outputs.

Decision: Keep raw, core, and mart layers.

Reason: Raw tables preserve auditability, core tables centralize cleaning, marts provide clean business-facing outputs.

Decision: Flag orphan payments instead of dropping them.

Reason: Dropping them hides source system issues. A `loan_exists` flag lets analysts exclude or investigate them explicitly.

Decision: First-seen-wins deduplication.

Reason: The observed duplicates are exact duplicates. For conflicting duplicates, the better production answer would be quarantine and review.

Decision: Treat naive timestamps as already canonical.

Reason: The source provides no timezone contract for naive timestamps. The limitation is documented.

## Strong Presenter Framing

Say this:

"I treated this as a messy-data problem, not a big-data problem. The key engineering choices were to preserve raw inputs, clean deterministically in a core layer, publish small analytical marts, and make the known data defects visible instead of quietly deleting them."

Avoid saying this:

"I used DuckDB because it was easy."

Better:

"I used DuckDB because the workload is local, analytical, and small enough that adding distributed infrastructure would create more operational surface area without improving correctness."
