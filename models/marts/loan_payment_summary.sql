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
FROM {{ ref('stg_loans') }} AS l
LEFT JOIN {{ ref('stg_payments') }} AS p
    ON l.loan_id = p.loan_id
GROUP BY
    l.loan_id,
    l.customer_id,
    l.product_type,
    l.status,
    l.principal_amount,
    l.interest_rate,
    l.term_months
