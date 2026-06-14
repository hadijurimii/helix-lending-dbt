SELECT 'raw.loans_raw' AS table_name, COUNT(*) AS row_count FROM raw.loans_raw
UNION ALL
SELECT 'raw.payments_raw', COUNT(*) FROM raw.payments_raw
UNION ALL
SELECT 'core.loans_clean', COUNT(*) FROM core.loans_clean
UNION ALL
SELECT 'core.payments_clean', COUNT(*) FROM core.payments_clean
UNION ALL
SELECT 'marts.dim_loans', COUNT(*) FROM marts.dim_loans
UNION ALL
SELECT 'marts.fact_payments', COUNT(*) FROM marts.fact_payments
UNION ALL
SELECT 'marts.loan_payment_summary', COUNT(*) FROM marts.loan_payment_summary;
