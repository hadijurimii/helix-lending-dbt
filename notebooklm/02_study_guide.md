# Study Guide: Understand The Project Cold

## Mental Model

Think of the project as a three-room factory:

1. Receiving room: land the raw files exactly enough to audit them.
2. Cleaning room: standardize types, categories, timestamps, and JSON.
3. Showroom: publish tables that analysts can actually query without stepping on broken glass.

The interview story is not "I wrote a script." It is "I made messy data trustworthy enough to query, while keeping the defects visible."

## The Core Narrative

The company needs answers about delinquency, inconsistent payments, freshness, and completeness. The source files are not clean enough to answer those questions directly.

The pipeline solves that by:

- preserving raw source data
- normalizing and typing records
- extracting useful nested fields
- deduplicating exact duplicate IDs
- flagging known quality issues
- producing query-ready outputs

## Architecture Walkthrough

`main.py` calls `run_pipeline(...)`.

`run_pipeline(...)` does five important things:

1. Creates output directories.
2. Opens the DuckDB database.
3. Registers parsing functions.
4. Runs `ingest`, `load`, and `transform`.
5. Writes run metrics and data quality output.

The database path is `output/helix_lending.duckdb`.

The Parquet files live under `output/parquet/`.

## What Happens In Ingest

Loan CSV is read with all columns as strings. This avoids breaking on weird values before the pipeline has a chance to inspect or clean them.

Payment JSONL is read with an explicit schema. This matters because auto inference mishandled mixed timestamp formats during testing.

Raw tables include:

- source fields
- source file path
- row number
- ingestion timestamp

## What Happens In Load

Load is where messy source data becomes typed and predictable.

Loan examples:

- `PERSONAL`, `Personal`, and `personal` become `personal`.
- `$155,069.87` becomes decimal `155069.87`.
- `11-Dec-2020`, `01/13/2020`, and `2024-06-01` become dates.
- borrower JSON is parsed only if valid.

Payment examples:

- `2024-06-30T03:58:00-08:00` becomes a UTC-normalized timestamp.
- nested payment method JSON becomes columns like `payment_method_type`.
- optional metadata becomes nullable metadata columns.

## What Happens In Transform

The mart layer is intentionally small:

- `dim_loans`: clean loan attributes.
- `fact_payments`: clean payment events.
- `loan_payment_summary`: one row per loan with payment aggregates.

The useful trick is `loan_exists` in `fact_payments`. It makes orphan payments obvious without deleting them.

## Data Quality Talking Points

The quality checks are direct SQL because the rules are small and explicit.

Four categories:

- freshness: how recent the ingested and event data is
- completeness: missing or malformed fields
- uniqueness: duplicate IDs removed
- referential integrity: payments that reference missing loans

Important numbers:

- `30` duplicate loans removed
- `30` duplicate payments removed
- `30` malformed borrower JSON rows
- `75` payments missing amount
- `100` orphan payments
- `7,405` payments missing metadata

## What To Say If Asked About dbt

The target GitHub repo is named `helix-lending-dbt`, but this implementation is Python plus DuckDB SQL.

Strong answer:

"I would move the core and mart SQL into dbt if this became a maintained analytics project. For this assessment, a Python entrypoint around DuckDB kept the pipeline easier to run and review. The layer boundaries already map cleanly to dbt models: raw sources, core staging models, and marts."

## What To Say If Asked About Airflow

Strong answer:

"Airflow would be useful when this has schedules, retries, dependencies, alerts, and multiple upstream systems. For a local take-home with two files, a clear entrypoint is better. I focused the production quality on deterministic transforms, quality checks, observability, and tests."

## What To Say If Asked About Deduplication

Strong answer:

"I used first-seen-wins because the duplicate examples were exact duplicates. If duplicates conflicted, I would not pick a winner silently. I would write conflicting records to quarantine with the duplicate group, source rows, and reason code."

## What To Say If Asked About Orphan Payments

Strong answer:

"I kept orphan payments and flagged them with `loan_exists = false`. Dropping them would improve the metric cosmetically but hide a source data issue. Analysts can exclude them for loan-level reporting while data engineering investigates the upstream integrity problem."

## What To Say If Asked About Naive Timestamps

Strong answer:

"Offset and Z timestamps are normalized to UTC. Naive timestamps are treated as already canonical because the source does not provide a timezone contract. I documented that limitation. In production, I would require source-level timezone semantics before claiming true UTC correctness."

## Weak Spots To Own

Own these directly:

- No quarantine tables yet.
- No incremental loading yet.
- No dbt project yet.
- Naive timestamps rely on a documented assumption.
- Delinquency logic is not fully modeled because expected payment schedules and grace periods are business rules not supplied by the dataset.

Do not apologize for them. Explain the tradeoff.

## Best 60-Second Explanation

"This is a local lending data pipeline built with Python and DuckDB. I ingest raw loans and payments into audit-friendly raw tables, load them into cleaned typed core tables, then publish a small mart layer with loan dimension, payment fact, and loan payment summary outputs. The important part is that the pipeline does not hide source issues: duplicates are counted, malformed borrower JSON is flagged, missing amounts remain visible, and orphan payments get a referential-integrity flag. I chose DuckDB because this is a messy-data assessment, not a big-data one. The implementation is small, testable, and easy to explain, which is exactly what I want in a take-home debrief."
