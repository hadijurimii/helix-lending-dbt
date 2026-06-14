# Data Lineage

## Source To Raw

| Source | Raw Table | Notes |
|---|---|---|
| `data/loans.csv` | `raw.loans_raw` | CSV is read as varchar to avoid premature type failures. |
| `data/payments.jsonl` | `raw.payments_raw` | JSONL is read with an explicit schema because timestamp inference is unsafe. |

## Raw To Core

| Raw Table | Core Table | Key Transformations |
|---|---|---|
| `raw.loans_raw` | `core.loans_clean` | Normalize casing, parse money, parse dates, validate borrower JSON, deduplicate by `loan_id`. |
| `raw.payments_raw` | `core.payments_clean` | Parse timestamps, flatten nested JSON, normalize method/source fields, deduplicate by `payment_id`. |

## Core To Marts

| Core Tables | Mart | Purpose |
|---|---|---|
| `core.loans_clean` | `marts.dim_loans` | Loan dimension for attributes and borrower snapshot fields. |
| `core.payments_clean` | `marts.fact_payments` | Payment fact table with `loan_exists` referential integrity flag. |
| `core.loans_clean`, `core.payments_clean` | `marts.loan_payment_summary` | Loan-level payment counts, amounts, first/last payment dates, invalid amount counts. |

## Quality Outputs

| Output | Purpose |
|---|---|
| `output/metrics/run_metrics.json` | Stage duration and row counts. |
| `output/metrics/data_quality_report.json` | Freshness, completeness, uniqueness, and referential integrity checks. |
