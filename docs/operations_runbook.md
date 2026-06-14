# Operations Runbook

## Local Run

```powershell
python main.py
```

## Test Run

```powershell
pytest -q
```

## Docker Run

```powershell
docker compose up --build helix-pipeline
```

## dbt Run

The dbt profile points to `output/helix_lending.duckdb`, so run the Python pipeline first.

```powershell
python main.py
dbt run --profiles-dir . --project-dir .
dbt test --profiles-dir . --project-dir .
```

## Expected Outputs

- `output/helix_lending.duckdb`
- `output/parquet/*.parquet`
- `output/metrics/run_metrics.json`
- `output/metrics/data_quality_report.json`

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| DuckDB JSON timestamp error | JSON auto inference was used | Use the pipeline's explicit JSON schema path. |
| Missing dbt source tables | Pipeline has not run yet | Run `python main.py` first. |
| Orphan payment count is non-zero | Source has payment rows without loan matches | Expected for current data; inspect `loan_exists = false`. |
| Malformed borrower JSON exists | Source contains invalid embedded JSON | Expected for current data; use `borrower_info_valid`. |
