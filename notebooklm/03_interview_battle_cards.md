# Interview Battle Cards

Use these as quick answers. Do not ramble. One confident paragraph beats five cautious ones.

## Why did you choose DuckDB?

Because the workload is local, analytical, and small. DuckDB gives SQL transforms, a queryable database artifact, and Parquet export without adding Spark, Airflow, or warehouse overhead. The assessment is about messy data quality, not distributed compute.

## Why not use dbt?

The layer design maps cleanly to dbt, but I kept the implementation as a runnable Python/DuckDB pipeline for assessment speed and simplicity. If this became a maintained analytics workflow, I would move `core` and `marts` SQL into dbt models and keep Python for ingestion and orchestration.

## Why keep raw tables?

Raw tables make the pipeline auditable. If a cleaned value looks wrong, I can trace it back to the source row, source file, and ingestion timestamp.

## Why first-seen-wins for duplicates?

The observed duplicate IDs were exact duplicate records, so first-seen-wins is acceptable for this dataset. If duplicate records conflicted, silently picking one would be bad engineering. I would quarantine those groups and require a business or source-system rule.

## Why flag orphan payments instead of dropping them?

Because orphan payments are a data quality signal. Dropping them would make the mart look cleaner while hiding a source integrity problem. The `loan_exists` flag lets analysts filter them out while preserving the evidence.

## How do you handle malformed borrower JSON?

The pipeline validates JSON first. Valid JSON is extracted into borrower columns; malformed JSON stays in `borrower_info_raw` with `borrower_info_valid = false`. That keeps the row usable without pretending the nested fields exist.

## How do you handle timestamps?

Offset and `Z` timestamps are normalized to UTC. Naive timestamps are treated as canonical because the source does not specify their timezone. I documented that limitation because fake certainty is worse than an honest assumption.

## What quality checks did you implement?

Freshness, completeness, uniqueness, and referential integrity. The quality report captures latest ingestion/event dates, missing values, malformed JSON, duplicate IDs removed, and payments without matching loans.

## What are the most important quality findings?

There are `30` duplicate loans, `30` duplicate payments, `30` malformed borrower JSON rows, `75` payments missing amount, `100` orphan payments, and `7,405` payments missing metadata.

## What would you improve first?

I would add quarantine tables for invalid records and conflicting duplicates. That gives operations a clear place to inspect bad records instead of burying quality issues in logs.

## What would you improve second?

Incremental loading. The current pipeline is full-refresh, which is fine for this dataset. For production, I would track source files, watermarks, and idempotent loads.

## How would you answer the delinquency question?

This pipeline prepares the data needed, but true delinquency needs a business definition: due dates, grace period, payment schedule, and whether loan status or payment behavior is canonical. I would add a schedule model before claiming a 30-day delinquency metric.

## What tests did you write?

Parser unit tests for date and timestamp handling, plus an end-to-end fixture covering deduplication, dollar amount parsing, JSON flattening, and orphan payment flagging.

## What was the hardest bug?

DuckDB JSON auto inference tried to be helpful and inferred timestamps too aggressively. That broke on mixed timestamp formats. The fix was explicit JSON schema during ingest and controlled parsing during load.

## What is the architecture in one sentence?

Raw preserves evidence, core standardizes truth, marts answer questions.

## What is the strongest design choice?

Making data defects visible. The pipeline does not hide missing amounts, malformed JSON, or orphan payments. It turns them into measurable quality signals.

## What is the riskiest assumption?

Naive timestamps. Without source timezone semantics, the pipeline can only treat them as canonical and document the assumption.

## What should you not say?

Do not say "I used DuckDB because it was easy." Say "I used DuckDB because it matches the workload and reduces unnecessary operational complexity."

Do not say "The data is clean now." Say "The data is standardized, modeled, and quality issues are explicitly reported."

Do not say "I removed bad data." Say "I preserved questionable data and flagged it where needed."
