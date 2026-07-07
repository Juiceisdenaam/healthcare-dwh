
WITH cleaned AS (
  SELECT
    patient_id,
    source_system,
    REPLACE(initials, '.', '') as initials,
    first_name,
    prefix,
    last_name,
    gender,
    birth_date,
    email_address,
    street_name,
    house_number,
    CAST(REGEXP_REPLACE(house_number, '[^0-9]', '', 'g') AS INTEGER) AS house_number_clean,
    house_number_addition,
    REPLACE(postal_code, ' ', '') as postal_code,
    city,
    gp_code,
    insurance_code,
    policy_number,
    personal_identification_number,
    registration_date,
    phone_number,
    regexp_replace(phone_number, '[^0-9]', '', 'g') as phone_digits
  FROM {{ ref('stg_epd_patients_combined') }}
), 
normalized AS (
  SELECT 
    *,
    case
        when phone_digits LIKE '06%' then '+31' || substring(phone_digits from 2)
        when phone_number LIKE '+31(0%' then '+31' || substring(phone_digits from 4)
        when phone_digits LIKE '31%' then '+' || substring(phone_digits from 1)
        when phone_digits LIKE '0%' then '+31' || substring(phone_digits from 2)
        else null
      end as phone_number_normalized,
    
  CASE
        -- If addition already exists → trust it
        WHEN house_number_addition IS NOT NULL 
             AND TRIM(house_number_addition) <> ''
        THEN UPPER(TRIM(house_number_addition))

        -- Else extract from house_number
        ELSE NULLIF(
            UPPER(REGEXP_REPLACE(house_number, '[0-9]', '', 'g')),
            ''
        )
    END AS house_number_addition_correct

    FROM cleaned
)
SELECT 
    * 
FROM normalized


