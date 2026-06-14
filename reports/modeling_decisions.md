# Modeling Decisions

## Chosen Model

The project uses a small star-style model:

- `dim_loans`
- `fact_payments`
- `loan_payment_summary`

## Why Not One Big Table

A one-big-table model would duplicate loan attributes across every payment and make referential issues easier to miss. Keeping payments as facts and loans as a dimension is cleaner for explainability and future extension.

## Why Keep A Summary Mart

`loan_payment_summary` gives fast answers to loan-level questions without forcing every consumer to rewrite the same aggregation logic.

## Future dbt Shape

If the project grows, the natural dbt layout is:

- `models/staging`: typed wrappers around `core` tables
- `models/marts`: analytical tables for reporting
- `models/marts/schema.yml`: tests for uniqueness, non-null keys, and accepted values
