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
FROM {{ source('core', 'loans_clean') }}
