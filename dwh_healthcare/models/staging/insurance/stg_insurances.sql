SELECT
    insurance_code,
    UPPER(TRIM(insurance_name)) AS insurance_name
FROM {{ source('healthcare', 'insurances') }}