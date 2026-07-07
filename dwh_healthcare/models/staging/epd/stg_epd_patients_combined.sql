SELECT
    *
FROM
    {{ ref('stg_epd_a_patients') }}

UNION ALL

SELECT
    *
FROM
    {{ ref('stg_epd_b_patients') }}

UNION ALL

SELECT
    *
FROM
    {{ ref('stg_epd_c_patients') }}