SELECT
    p.*,
    l.loan_id IS NOT NULL AS loan_exists
FROM {{ ref('stg_payments') }} AS p
LEFT JOIN {{ ref('stg_loans') }} AS l
    ON p.loan_id = l.loan_id
