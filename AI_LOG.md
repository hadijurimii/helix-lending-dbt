# AI Collaboration Log

## Tools Used

- Codex: repository inspection, data profiling, pipeline implementation, README drafting, and test scaffolding.

## Major Prompts

### Prompt 1

**Asked:** Summarize the project and implement the data engineering parts from ingest to load to transform.

**Got:** A suggested local Python/DuckDB pipeline with raw, core, and mart layers.

**Did:** Used the direction, then verified the actual data before writing the pipeline.

### Prompt 2

**Asked:** Inspect the shape and quality of `loans.csv` and `payments.jsonl`.

**Got:** Counts for duplicate IDs, mixed date formats, missing values, malformed borrower JSON, optional metadata, and orphan payment references.

**Did:** Used the profile to choose the cleaning rules and quality checks.

### Prompt 3

**Asked:** Build a minimal runnable pipeline for ingest, load, and transform.

**Got:** A Python entrypoint, DuckDB SQL stages, structured logging, metrics, and Parquet exports.

**Did:** Implemented the pipeline and iterated against real runtime failures.

### Prompt 4

**Asked:** Add focused tests for risky transformation logic.

**Got:** Parser unit tests and a small end-to-end fixture.

**Did:** Kept the tests narrow and tied to actual failure modes: dates, timestamps, deduplication, amount parsing, JSON flattening, and orphan payments.

## Where The AI Was Wrong, Incomplete, Or Wrong-But-Plausible

### Example 1

**Context:** Initial load logic extracted fields from `borrower_info` directly.

**What the AI suggested:** Use JSON extraction on the embedded borrower JSON column.

**What was wrong with it:** Some borrower JSON is malformed, so direct extraction failed the run.

**How I caught it:** The full pipeline run crashed on malformed JSON.

**What I did instead:** Added `json_valid` handling and only extracted borrower fields for valid JSON. Invalid JSON remains auditable via `borrower_info_raw` and `borrower_info_valid`.

### Example 2

**Context:** Payment JSON ingestion originally used DuckDB's automatic schema inference.

**What the AI suggested:** Use `read_json_auto` for the JSONL file.

**What was wrong with it:** It inferred timestamps too aggressively and failed when fixture rows mixed `Z` and offset timestamps.

**How I caught it:** The end-to-end test failed during ingest.

**What I did instead:** Pinned the JSON schema explicitly and parsed timestamps in the controlled load step.

### Example 3

**Context:** Principal amount parsing initially removed commas.

**What the AI suggested:** `replace(principal_amount, ',', '')`.

**What was wrong with it:** Some values also include `$`, leaving valid principal amounts as null.

**How I caught it:** A quality query showed 1,429 null principal amounts after load.

**What I did instead:** Used a regex to strip both `$` and commas before casting.

## Where I Overrode The AI's Suggestion

### Override 1

**The AI suggested:** A broader orchestration and quality-framework setup would look more "production".

**I chose instead:** A plain `main.py`, DuckDB SQL, JSON logs, and direct SQL quality checks.

**Reasoning:** This dataset is about 85k rows. Airflow, Dagster, Spark, or a full quality framework would add ceremony without improving the answer. The stronger engineering choice is a small pipeline that is easy to run, inspect, and explain.

## Reflection

I trusted the AI for acceleration, not judgment. It was useful for laying out a pragmatic pipeline shape, drafting boilerplate, and quickly generating tests around parser behavior. I did not trust it with the source data assumptions. The actual files had the important details: malformed JSON, mixed timestamp formats, dollar-formatted amounts, duplicate IDs, missing metadata, and orphan payments. Those needed profiling and runtime verification, not confident prose.

The most useful pattern was asking the AI to build a first version, then forcing that version through the real data and tests. The failures were productive because they exposed hidden assumptions. The weakest AI behavior was reaching for generic "production" advice: orchestration, frameworks, and abstractions that would look busy but not make this small assessment better. If I did this again, I would still use AI heavily, but I would profile the data even earlier and make every model suggestion earn its place against observed rows.
