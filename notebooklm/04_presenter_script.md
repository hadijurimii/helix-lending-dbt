# Presenter Script

## Opening

"I treated this assessment as a messy-data engineering problem. The goal was not to build a huge platform; it was to land two unreliable sources, make them queryable, and expose quality issues clearly."

## Slide 1: Title

"The pipeline takes loan originations and payment events through raw, core, and mart layers. The final outputs are DuckDB and Parquet, with metrics and quality reports generated on every run."

## Slide 2: The Real Problem

"The source files are small, but they are messy in realistic ways: duplicate IDs, mixed casing, mixed date formats, malformed embedded JSON, missing payment amounts, optional metadata, and orphan payments. So the main engineering problem is trust, not scale."

## Slide 3: Architecture

"I used a three-layer model. Raw preserves the evidence. Core standardizes types and structure. Marts publish tables that are easy to query. This makes the flow explainable and keeps auditability intact."

## Slide 4: Ingest

"Ingest keeps the data close to source. Loan CSV is read as strings. Payment JSON uses an explicit schema because auto inference broke on mixed timestamp formats. I want parsing rules in the load step, where they are visible and testable."

## Slide 5: Load

"Load handles normalization: casing, dollar amounts, dates, timestamps, nested JSON, and deduplication. The important decision is that malformed borrower JSON does not kill the row. It becomes a flag and nullable parsed fields."

## Slide 6: Transform

"The mart layer has a loan dimension, payment fact, and loan payment summary. I also keep a `loan_exists` flag on payments. That means orphan payments remain available for investigation instead of being dropped."

## Slide 7: Quality Findings

"The latest run removed 30 duplicate loans and 30 duplicate payments. It found 30 malformed borrower JSON rows, 75 payments missing amount, 100 orphan payments, and 7,405 payments missing metadata. These are not hidden; they are reported."

## Slide 8: Observability And Tests

"Every run emits JSON logs and writes metrics by stage. Tests cover parser behavior and a small end-to-end fixture. The test caught a real issue with JSON timestamp inference, which led to the explicit schema decision."

## Slide 9: Tradeoffs

"I did not add Airflow, Spark, or a quality framework because the workload does not justify it. The next production steps would be quarantine tables, incremental loads, and potentially dbt models for the SQL layers."

## Slide 10: Close

"The result is a small but defensible pipeline: easy to run, easy to inspect, and honest about data defects. That is the core of the design."

## Closing Line

"If I had to extend it live, I would start with quarantine tables or a dbt refactor, because the current layer boundaries already support both."
