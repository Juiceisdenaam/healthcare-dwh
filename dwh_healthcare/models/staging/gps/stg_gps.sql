SELECT
    gp_code,
    UPPER(TRIM(gp_name)) AS gp_name,
    UPPER(TRIM(practice_name)) AS practice_name,
    agb_code,
    UPPER(TRIM(city)) AS city,
    upper(regexp_replace(trim(postal_code), '\s+', '', 'g')) AS postal_code,
    created_at::TIMESTAMP AS created_at
FROM {{ source('healthcare', 'gps') }}