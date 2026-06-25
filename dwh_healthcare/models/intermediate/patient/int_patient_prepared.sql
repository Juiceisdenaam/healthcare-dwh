
WITH cleaned AS (
  SELECT
    patient_id,
    source_system,
    initials,
    first_name,
    prefix,
    last_name,
    gender,
    birth_date,
    email_address,
    street_name,
    house_number,
    house_number_addition,
    postal_code,
    city,
    gp_code,
    insurance_code,
    policy_number,
    personal_identification_number,
    registration_date,
    phone_number,
    regexp_replace(phone_number, '[^0-9]', '', 'g') as phone_digits
  FROM {{ ref('stg_epd_patients') }}
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
      end as phone_number_normalized
    FROM cleaned
)
SELECT 
    * 
FROM normalized


