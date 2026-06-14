# Architecture

## Design Principle

This project treats the assessment as a messy-data problem, not a big-data problem. The goal is to keep the pipeline small, inspectable, and honest about defects.

## Layers

| Layer | Purpose | Tables |
|---|---|---|
| `raw` | Land source data with minimal interpretation | `raw.loans_raw`, `raw.payments_raw` |
| `core` | Clean, type, deduplicate, and normalize source records | `core.loans_clean`, `core.payments_clean` |
| `marts` | Publish query-ready analytical outputs | `marts.dim_loans`, `marts.fact_payments`, `marts.loan_payment_summary` |

## Flow

1. `main.py` builds path config and opens `output/helix_lending.duckdb`.
2. `ingest` reads `data/loans.csv` and `data/payments.jsonl`.
3. `load` standardizes source records and creates typed core tables.
4. `transform` publishes analytical marts.
5. `write_quality_report` writes freshness, completeness, uniqueness, and referential integrity checks.

## Why DuckDB

DuckDB is the right fit for a local analytical pipeline with around 85k input rows. It gives SQL transforms, a portable database file, and Parquet export without pretending this needs Spark.

## Why dbt Is Included

The original implementation keeps SQL inside the Python pipeline for a simple runnable assessment. The added dbt files show how the cleaned DuckDB outputs can be wrapped as dbt staging and mart models if the project becomes a maintained analytics repo.
