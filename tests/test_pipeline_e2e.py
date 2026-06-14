import json
from pathlib import Path

import duckdb

from src.helix_pipeline.config import PipelinePaths
from src.helix_pipeline.pipeline import run_pipeline


def test_pipeline_runs_end_to_end_on_small_fixture(tmp_path: Path) -> None:
    project_root = tmp_path
    data_dir = project_root / "data"
    data_dir.mkdir()

    (data_dir / "loans.csv").write_text(
        "\n".join(
            [
                "loan_id,customer_id,product_type,principal_amount,interest_rate,term_months,origination_date,origination_channel,status,borrower_info",
                'L1,C1,PERSONAL,"$12,000.50",7.5,36,2024-01-31,online,active,"{""credit_score"": 720, ""employment"": ""salaried"", ""annual_income"": 80000, ""years_employed"": 5}"',
                'L1,C1,PERSONAL,"$12,000.50",7.5,36,2024-01-31,online,active,"{""credit_score"": 720, ""employment"": ""salaried"", ""annual_income"": 80000, ""years_employed"": 5}"',
                'L2,C2,Student,5400,5.1,24,02/28/2024,branch,closed,"{""credit_score"": 660, ""employment"": ""self-employed"", ""annual_income"": 45000, ""years_employed"": 2}"',
            ]
        ),
        encoding="utf-8",
    )
    (data_dir / "payments.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "payment_id": "P1",
                        "loan_id": "L1",
                        "amount": 100.25,
                        "timestamp": "2024-02-01T10:00:00-05:00",
                        "payment_method": {"type": "ACH", "details": {"last_four": "1234", "bank": "Helix First"}},
                        "metadata": {"source": "web", "user_agent": "Agent/1.0"},
                    }
                ),
                json.dumps(
                    {
                        "payment_id": "P1",
                        "loan_id": "L1",
                        "amount": 100.25,
                        "timestamp": "2024-02-01T10:00:00-05:00",
                        "payment_method": {"type": "ACH", "details": {"last_four": "1234", "bank": "Helix First"}},
                        "metadata": {"source": "web", "user_agent": "Agent/1.0"},
                    }
                ),
                json.dumps(
                    {
                        "payment_id": "P2",
                        "loan_id": "L3",
                        "amount": None,
                        "timestamp": "2024-02-02T12:00:00Z",
                        "payment_method": {"type": "card", "details": {"last_four": None, "bank": None}},
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    run_pipeline(PipelinePaths.from_project_root(project_root))

    output_db = project_root / "output" / "helix_lending.duckdb"
    with duckdb.connect(str(output_db)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM core.loans_clean").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM core.payments_clean").fetchone()[0] == 2
        assert connection.execute("SELECT principal_amount FROM core.loans_clean WHERE loan_id = 'L1'").fetchone()[0] == 12000.50
        assert connection.execute("SELECT payment_method_type FROM core.payments_clean WHERE payment_id = 'P1'").fetchone()[0] == "ach"
        assert connection.execute("SELECT loan_exists FROM marts.fact_payments WHERE payment_id = 'P2'").fetchone()[0] is False
