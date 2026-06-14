# Interview Debrief Notes

## Opening Pitch

I treated the assessment as a messy-data engineering problem. The pipeline lands raw source data, standardizes it into typed core tables, publishes analytical marts, and reports source quality issues instead of hiding them.

## Strong Architecture Defense

DuckDB is the right engine here because the workload is local and analytical. The data size does not justify distributed compute. The engineering effort belongs in deterministic parsing, lineage, quality reporting, and tests.

## Design Choices To Highlight

- Raw tables preserve evidence.
- Core tables centralize cleaning and typing.
- Marts keep analysis simple.
- Orphan payments are flagged with `loan_exists`, not dropped.
- Malformed borrower JSON is retained and flagged.
- Duplicate IDs are deduplicated first-seen because observed duplicates are exact duplicates.

## Questions To Expect

### Why not Spark?

Because the input is roughly 85k rows. Spark would add operational weight without improving correctness.

### Why not Airflow?

Airflow is useful for schedules, retries, dependency graphs, and alerting. This assessment only needs a clear local entrypoint.

### Why not dbt from the start?

The layer boundaries already map to dbt. I kept Python/DuckDB first for a compact runnable assessment, then added dbt wrappers to show the migration path.

### What is the biggest limitation?

Naive timestamps. Without a source timezone contract, the pipeline treats them as canonical and documents the assumption.
