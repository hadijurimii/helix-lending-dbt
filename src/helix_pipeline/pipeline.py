from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from src.helix_pipeline.config import PipelinePaths
from src.helix_pipeline.logging_utils import get_logger
from src.helix_pipeline.parsers import parse_origination_date, parse_timestamp_utc


logger = get_logger()


@dataclass(frozen=True)
class StepMetric:
    step: str
    started_at: str
    finished_at: str
    duration_seconds: float
    rows_in: int
    rows_out: int


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Helix Lending pipeline.")
    parser.add_argument(
        "--project-root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="Root directory that contains data/ and receives output/.",
    )
    args = parser.parse_args()

    run_pipeline(PipelinePaths.from_project_root(args.project_root))
    return 0


def run_pipeline(paths: PipelinePaths) -> None:
    paths.create_directories()
    run_started_at = datetime.now(timezone.utc).isoformat()

    with duckdb.connect(str(paths.database_path)) as connection:
        register_functions(connection)
        bootstrap_schemas(connection)

        metrics = [
            ingest(connection, paths),
            load(connection, paths),
            transform(connection, paths),
        ]
        quality_report_path = write_quality_report(connection, paths)

    metrics_payload = {
        "run_started_at": run_started_at,
        "run_finished_at": datetime.now(timezone.utc).isoformat(),
        "database_path": str(paths.database_path),
        "quality_report_path": str(quality_report_path),
        "steps": [metric.__dict__ for metric in metrics],
    }
    metrics_path = paths.metrics_dir / "run_metrics.json"
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    logger.info(
        "Pipeline run completed",
        extra={
            "event": "pipeline.completed",
            "context": {
                "database_path": str(paths.database_path),
                "metrics_path": str(metrics_path),
            },
        },
    )


def register_functions(connection: duckdb.DuckDBPyConnection) -> None:
    connection.create_function(
        "parse_origination_date",
        parse_origination_date,
        ["VARCHAR"],
        "DATE",
    )
    connection.create_function(
        "parse_timestamp_utc",
        parse_timestamp_utc,
        ["VARCHAR"],
        "TIMESTAMP",
    )


def bootstrap_schemas(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    connection.execute("CREATE SCHEMA IF NOT EXISTS core;")
    connection.execute("CREATE SCHEMA IF NOT EXISTS marts;")


def ingest(connection: duckdb.DuckDBPyConnection, paths: PipelinePaths) -> StepMetric:
    started_at = datetime.now(timezone.utc).isoformat()
    step_started = time.perf_counter()
    loans_path = paths.data_dir / "loans.csv"
    payments_path = paths.data_dir / "payments.jsonl"

    logger.info(
        "Starting ingest",
        extra={
            "event": "ingest.started",
            "context": {
                "loans_path": str(loans_path),
                "payments_path": str(payments_path),
            },
        },
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE raw.loans_raw AS
        SELECT
            row_number() OVER () AS raw_row_number,
            loan_id,
            customer_id,
            product_type,
            principal_amount,
            interest_rate,
            term_months,
            origination_date,
            origination_channel,
            status,
            borrower_info,
            current_timestamp AS ingested_at,
            ? AS source_file
        FROM read_csv(?, header = true, all_varchar = true);
        """,
        [str(loans_path), str(loans_path)],
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE raw.payments_raw AS
        SELECT
            row_number() OVER () AS raw_row_number,
            payment_id,
            loan_id,
            amount,
            timestamp,
            payment_method,
            metadata,
            current_timestamp AS ingested_at,
            ? AS source_file
        FROM read_json(
            ?,
            columns = {
                payment_id: 'VARCHAR',
                loan_id: 'VARCHAR',
                amount: 'DOUBLE',
                timestamp: 'VARCHAR',
                payment_method: 'JSON',
                metadata: 'JSON'
            },
            format = 'newline_delimited'
        );
        """,
        [str(payments_path), str(payments_path)],
    )

    export_table(connection, "raw.loans_raw", paths.parquet_dir / "raw_loans.parquet")
    export_table(connection, "raw.payments_raw", paths.parquet_dir / "raw_payments.parquet")

    loans_rows = scalar(connection, "SELECT COUNT(*) FROM raw.loans_raw;")
    payments_rows = scalar(connection, "SELECT COUNT(*) FROM raw.payments_raw;")
    finished_at = datetime.now(timezone.utc).isoformat()
    duration_seconds = round(time.perf_counter() - step_started, 3)

    logger.info(
        "Finished ingest",
        extra={
            "event": "ingest.finished",
            "context": {
                "loans_rows": loans_rows,
                "payments_rows": payments_rows,
                "duration_seconds": duration_seconds,
            },
        },
    )

    return StepMetric(
        step="ingest",
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        rows_in=loans_rows + payments_rows,
        rows_out=loans_rows + payments_rows,
    )


def load(connection: duckdb.DuckDBPyConnection, paths: PipelinePaths) -> StepMetric:
    started_at = datetime.now(timezone.utc).isoformat()
    step_started = time.perf_counter()
    logger.info("Starting load", extra={"event": "load.started", "context": {}})

    connection.execute(
        """
        CREATE OR REPLACE TABLE core.loans_clean AS
        WITH ranked AS (
            SELECT
                *,
                row_number() OVER (PARTITION BY loan_id ORDER BY raw_row_number) AS loan_rank
            FROM raw.loans_raw
        ),
        prepared AS (
            SELECT
                *,
                json_valid(borrower_info) AS borrower_info_valid
            FROM ranked
        )
        SELECT
            loan_id,
            NULLIF(trim(customer_id), '') AS customer_id,
            lower(trim(product_type)) AS product_type,
            TRY_CAST(regexp_replace(principal_amount, '[$,]', '', 'g') AS DECIMAL(18, 2)) AS principal_amount,
            TRY_CAST(interest_rate AS DECIMAL(8, 4)) AS interest_rate,
            TRY_CAST(term_months AS INTEGER) AS term_months,
            parse_origination_date(origination_date) AS origination_date,
            lower(trim(origination_channel)) AS origination_channel,
            lower(trim(status)) AS status,
            borrower_info AS borrower_info_raw,
            borrower_info_valid,
            CASE
                WHEN borrower_info_valid THEN TRY_CAST(json_extract_string(borrower_info, '$.credit_score') AS INTEGER)
                ELSE NULL
            END AS borrower_credit_score,
            CASE
                WHEN borrower_info_valid THEN lower(json_extract_string(borrower_info, '$.employment'))
                ELSE NULL
            END AS borrower_employment,
            CASE
                WHEN borrower_info_valid THEN TRY_CAST(json_extract_string(borrower_info, '$.annual_income') AS DECIMAL(18, 2))
                ELSE NULL
            END AS borrower_annual_income,
            CASE
                WHEN borrower_info_valid THEN TRY_CAST(json_extract_string(borrower_info, '$.years_employed') AS INTEGER)
                ELSE NULL
            END AS borrower_years_employed,
            ingested_at,
            source_file,
            raw_row_number
        FROM prepared
        WHERE loan_rank = 1;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE core.payments_clean AS
        WITH ranked AS (
            SELECT
                *,
                row_number() OVER (PARTITION BY payment_id ORDER BY raw_row_number) AS payment_rank
            FROM raw.payments_raw
        )
        SELECT
            payment_id,
            loan_id,
            TRY_CAST(amount AS DECIMAL(18, 2)) AS amount,
            parse_timestamp_utc(timestamp) AS payment_timestamp_utc,
            timestamp AS payment_timestamp_raw,
            lower(json_extract_string(payment_method, '$.type')) AS payment_method_type,
            json_extract_string(payment_method, '$.details.last_four') AS payment_method_last_four,
            json_extract_string(payment_method, '$.details.bank') AS payment_method_bank,
            lower(json_extract_string(metadata, '$.source')) AS metadata_source,
            json_extract_string(metadata, '$.user_agent') AS metadata_user_agent,
            metadata IS NOT NULL AS metadata_present,
            ingested_at,
            source_file,
            raw_row_number
        FROM ranked
        WHERE payment_rank = 1;
        """
    )

    export_table(connection, "core.loans_clean", paths.parquet_dir / "core_loans_clean.parquet")
    export_table(connection, "core.payments_clean", paths.parquet_dir / "core_payments_clean.parquet")

    rows_in = scalar(connection, "SELECT COUNT(*) FROM raw.loans_raw;") + scalar(
        connection, "SELECT COUNT(*) FROM raw.payments_raw;"
    )
    rows_out = scalar(connection, "SELECT COUNT(*) FROM core.loans_clean;") + scalar(
        connection, "SELECT COUNT(*) FROM core.payments_clean;"
    )
    finished_at = datetime.now(timezone.utc).isoformat()
    duration_seconds = round(time.perf_counter() - step_started, 3)

    logger.info(
        "Finished load",
        extra={
            "event": "load.finished",
            "context": {
                "rows_in": rows_in,
                "rows_out": rows_out,
                "duration_seconds": duration_seconds,
            },
        },
    )

    return StepMetric(
        step="load",
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        rows_in=rows_in,
        rows_out=rows_out,
    )


def transform(connection: duckdb.DuckDBPyConnection, paths: PipelinePaths) -> StepMetric:
    started_at = datetime.now(timezone.utc).isoformat()
    step_started = time.perf_counter()
    logger.info("Starting transform", extra={"event": "transform.started", "context": {}})

    connection.execute(
        """
        CREATE OR REPLACE TABLE marts.dim_loans AS
        SELECT
            loan_id,
            customer_id,
            product_type,
            principal_amount,
            interest_rate,
            term_months,
            origination_date,
            origination_channel,
            status,
            borrower_credit_score,
            borrower_employment,
            borrower_annual_income,
            borrower_years_employed
        FROM core.loans_clean;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE marts.fact_payments AS
        SELECT
            payment_id,
            p.loan_id,
            amount,
            payment_timestamp_utc,
            payment_method_type,
            payment_method_last_four,
            payment_method_bank,
            metadata_source,
            metadata_user_agent,
            l.loan_id IS NOT NULL AS loan_exists
        FROM core.payments_clean AS p
        LEFT JOIN core.loans_clean AS l
            ON p.loan_id = l.loan_id;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE marts.loan_payment_summary AS
        SELECT
            l.loan_id,
            l.customer_id,
            l.product_type,
            l.status,
            l.principal_amount,
            l.interest_rate,
            l.term_months,
            COUNT(p.payment_id) AS payment_count,
            COALESCE(SUM(p.amount), 0) AS total_paid_amount,
            MIN(p.payment_timestamp_utc) AS first_payment_at_utc,
            MAX(p.payment_timestamp_utc) AS last_payment_at_utc,
            SUM(CASE WHEN p.payment_id IS NOT NULL AND p.amount IS NULL THEN 1 ELSE 0 END) AS invalid_payment_amount_count
        FROM core.loans_clean AS l
        LEFT JOIN core.payments_clean AS p
            ON l.loan_id = p.loan_id
        GROUP BY ALL;
        """
    )

    export_table(connection, "marts.dim_loans", paths.parquet_dir / "dim_loans.parquet")
    export_table(connection, "marts.fact_payments", paths.parquet_dir / "fact_payments.parquet")
    export_table(
        connection,
        "marts.loan_payment_summary",
        paths.parquet_dir / "loan_payment_summary.parquet",
    )

    rows_in = scalar(connection, "SELECT COUNT(*) FROM core.loans_clean;") + scalar(
        connection, "SELECT COUNT(*) FROM core.payments_clean;"
    )
    rows_out = scalar(connection, "SELECT COUNT(*) FROM marts.dim_loans;") + scalar(
        connection, "SELECT COUNT(*) FROM marts.fact_payments;"
    )
    finished_at = datetime.now(timezone.utc).isoformat()
    duration_seconds = round(time.perf_counter() - step_started, 3)

    logger.info(
        "Finished transform",
        extra={
            "event": "transform.finished",
            "context": {
                "rows_in": rows_in,
                "rows_out": rows_out,
                "duration_seconds": duration_seconds,
            },
        },
    )

    return StepMetric(
        step="transform",
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        rows_in=rows_in,
        rows_out=rows_out,
    )


def write_quality_report(connection: duckdb.DuckDBPyConnection, paths: PipelinePaths) -> Path:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "freshness": {
            "latest_loan_ingested_at": value(connection, "SELECT MAX(ingested_at) FROM raw.loans_raw;"),
            "latest_payment_ingested_at": value(connection, "SELECT MAX(ingested_at) FROM raw.payments_raw;"),
            "latest_origination_date": value(connection, "SELECT MAX(origination_date) FROM core.loans_clean;"),
            "latest_payment_timestamp_utc": value(
                connection,
                "SELECT MAX(payment_timestamp_utc) FROM core.payments_clean;",
            ),
        },
        "completeness": {
            "loans_missing_customer_id": scalar(
                connection,
                "SELECT COUNT(*) FROM core.loans_clean WHERE customer_id IS NULL;",
            ),
            "loans_with_malformed_borrower_info": scalar(
                connection,
                "SELECT COUNT(*) FROM core.loans_clean WHERE NOT borrower_info_valid;",
            ),
            "payments_missing_amount": scalar(
                connection,
                "SELECT COUNT(*) FROM core.payments_clean WHERE amount IS NULL;",
            ),
            "payments_missing_metadata": scalar(
                connection,
                "SELECT COUNT(*) FROM core.payments_clean WHERE NOT metadata_present;",
            ),
        },
        "uniqueness": {
            "duplicate_loan_ids_removed": scalar(
                connection,
                "SELECT (SELECT COUNT(*) FROM raw.loans_raw) - (SELECT COUNT(*) FROM core.loans_clean);",
            ),
            "duplicate_payment_ids_removed": scalar(
                connection,
                "SELECT (SELECT COUNT(*) FROM raw.payments_raw) - (SELECT COUNT(*) FROM core.payments_clean);",
            ),
        },
        "referential_integrity": {
            "payments_without_matching_loan": scalar(
                connection,
                "SELECT COUNT(*) FROM marts.fact_payments WHERE NOT loan_exists;",
            ),
        },
    }

    report_path = paths.metrics_dir / "data_quality_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    logger.info(
        "Wrote data quality report",
        extra={
            "event": "quality_report.written",
            "context": {"quality_report_path": str(report_path)},
        },
    )
    return report_path


def export_table(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    destination: Path,
) -> None:
    connection.execute(
        f"COPY {table_name} TO '{destination.as_posix()}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE);"
    )


def scalar(connection: duckdb.DuckDBPyConnection, query: str) -> int:
    return int(connection.execute(query).fetchone()[0])


def value(connection: duckdb.DuckDBPyConnection, query: str) -> object:
    return connection.execute(query).fetchone()[0]
