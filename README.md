# Helix Lending — Data Engineering Take-Home Assessment

Welcome, and thank you for taking the time to do this.

This is a **short, intense** take-home exercise designed to fit into roughly
**4–5 hours of focused work over a 2-day window**. We've timed and calibrated it.

If you find yourself well past that, stop and submit what you have with a note
in your README about what you would have completed with more time. We won't
penalize you for stopping; we will absolutely notice if you padded with
busywork.

---

## The scenario

You've just joined the data platform team at **Helix Lending**, a fictional
consumer lending company. Your first sprint task: stand up a small but
production-quality pipeline that lands clean, modeled, queryable data from
two messy sources.

The business needs this data to answer questions like:

- What is our 30-day delinquency rate by loan product?
- Which customers have payments inconsistent with their loan terms?
- What is the data freshness and completeness for each source?

---

## What we're giving you

Inside the `data/` folder:

- `loans.csv` — ~10,000 loan origination records. Mixed quality: type
  inconsistencies, duplicates, embedded JSON in one column, occasional
  oddities.
- `payments.jsonl` — newline-delimited JSON of payment events. Nested
  structures. Some events have missing fields. Timestamps in mixed timezones.
- `data_dictionary.md` — **partial**. Some columns are undocumented on
  purpose. Decide and document.

---

## What you must deliver

1. **A working pipeline** that ingests both sources, transforms them, and
   lands a modeled output (your choice of star schema, one-big-table, or
   other — but you must justify the choice in your README).

2. **Data quality checks.** At minimum, freshness, completeness, uniqueness,
   and referential integrity across the sources. Use any framework or write
   your own; defend the choice.

3. **Observability.** Structured logging, run metrics (rows in/out, duration,
   failures), and basic lineage documentation. We need to know what happened
   on every run.

4. **Tests.** Unit tests for transformation logic and at least one end-to-end
   test on a small fixture.

5. **A README** that explains: how to run it, your architectural choices and
   why, known limitations, and what you would do with more time.

6. **An AI Collaboration Log** (`AI_LOG.md`) — see below. **Mandatory.**

---

## Tech expectations

- **Language:** Python preferred; SQL where appropriate. Other languages (Rust,
  Go, Scala) allowed if you justify it in the README.
- **Storage:** Local files (Parquet/DuckDB) are fine. Cloud is not required
  and not extra credit.
- **Orchestration:** Optional. A clean `main.py` is acceptable; a real DAG
  (Airflow, Prefect, Dagster) is better if sensibly scoped for this size.
- **Libraries:** No restrictions, but every dependency you add costs you a
  sentence of justification in the README.

---

## GenAI usage — explicit expectations

**You are expected and encouraged to use GenAI tools** (ChatGPT, GitHub
Copilot, Cursor, Cline, Codeium, any LLM assistant or agent). Candidates who
do not use GenAI will not be able to complete this task in the time given.
*That is intentional.* We are hiring engineers who use AI well — not
engineers who avoid it, and not engineers who paste output unchecked.

You **must** submit an **AI Collaboration Log** (`AI_LOG.md`) containing:

- The major prompts you ran and which tool(s) you used.
- **At least 2 examples** where the AI was wrong, incomplete, or
  wrong-but-plausible, and how you caught it.
- **At least 1 architectural or design decision** you overrode the AI's
  suggestion on, and why.
- A **150–200 word reflection**: where did you trust AI in this work? Where
  did you refuse to? Why?

We will read this log carefully. It is weighted heavily.
**Submissions without it will not be evaluated.**

A template is provided in `AI_LOG_TEMPLATE.md`. Use it or write your own
format.

---

## What's not allowed

- Copying a public reference implementation of this exercise (we will check).
- Submitting AI output you cannot explain — see the live debrief below.

---

## Submission format

A git repository (private GitHub link) or zip archive containing:

```
your-submission/
├── src/                 your pipeline code
├── tests/               your tests
├── output/              final modeled data (Parquet or DuckDB file)
├── README.md
└── AI_LOG.md
```

---

## Live debrief

After submission, we will allocate **30-minutes** during your first round interview
to walk us through your solution, we might ask you to extend or modify a piece live, and
we'll discuss your AI log.

The debrief is where we calibrate the take-home against the live signal. We
take it seriously and so should you.

---

## Questions?

Reply to the email this assessment was sent with. We're not gatekeepers —
ask if anything is genuinely ambiguous. The data dictionary is deliberately
partial; do not ask us to fill it in. Decide and document.

Good luck.
