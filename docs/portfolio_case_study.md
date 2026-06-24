# Lending Data Quality and Payment Analysis

## The problem

Loan and payment data is only useful when analysts can trust it. This project processes raw lending files that contain duplicate records, inconsistent formats, malformed nested data, missing amounts, and payments that do not match a known loan.

The goal was not to make the source look perfect. It was to produce clean, queryable tables while keeping the evidence of data problems visible.

## What I built

I created a reproducible Python, SQL, and DuckDB workflow that:

1. Lands the original loan and payment data in raw tables.
2. Standardises amounts, dates, categories, and nested JSON into typed clean tables.
3. Removes exact duplicate records using an explicit first-seen rule.
4. Preserves quality flags for malformed borrower details, missing payment amounts, and unmatched payments.
5. Publishes analyst-ready loan, payment, and loan-level payment-summary tables as DuckDB and Parquet outputs.

## Results

| Measure | Result |
|---|---:|
| Raw loan records processed | 10,030 |
| Clean loan records published | 10,000 |
| Raw payment events processed | 74,786 |
| Clean payment events published | 74,756 |
| Duplicate loan records identified | 30 |
| Duplicate payment records identified | 30 |
| Payments without a matching loan flagged | 100 |
| Missing payment amounts flagged | 75 |

## Tools

Python, DuckDB, SQL, Parquet, dbt (optional modeling layer), and pytest.

## Why it matters

The output is suitable for business analysis because quality failures are measured rather than hidden. An analyst can use the final summary tables immediately, while a data owner can see exactly what must be fixed upstream.

## Deliverables

- Cleaned and typed datasets in Parquet
- Queryable DuckDB data marts
- Loan-level payment summary table
- Structured data-quality report
- Reproducible code and automated tests
