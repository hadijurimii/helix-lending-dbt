# Data Quality Summary

Generated from the latest full run.

| Check Area | Finding | Count |
|---|---:|---:|
| Uniqueness | Duplicate loan IDs removed | 30 |
| Uniqueness | Duplicate payment IDs removed | 30 |
| Completeness | Missing customer IDs | 10 |
| Completeness | Malformed borrower JSON | 30 |
| Completeness | Missing payment amounts | 75 |
| Completeness | Missing payment metadata | 7,405 |
| Referential integrity | Payments without matching loans | 100 |

## Interpretation

The pipeline makes the known defects explicit. The mart layer is queryable, but analysts should decide whether to exclude `loan_exists = false` payment rows depending on the business question.

## Recommended Follow-Up

- Add quarantine tables for malformed JSON, missing payment amounts, and orphan payments.
- Add a severity level and owner for each quality rule.
- Add CI checks that fail on unexpected increases in critical defects.
