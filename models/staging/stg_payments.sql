SELECT
    payment_id,
    loan_id,
    amount,
    payment_timestamp_utc,
    payment_method_type,
    payment_method_last_four,
    payment_method_bank,
    metadata_source,
    metadata_user_agent
FROM {{ source('core', 'payments_clean') }}
