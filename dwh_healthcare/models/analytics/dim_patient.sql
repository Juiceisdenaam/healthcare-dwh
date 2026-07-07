
with golden_records as (

    select 
        cluster_id,
        patient_id as master_patient_id,
        {{ dbt_utils.generate_surrogate_key(['cluster_id']) }}as patient_sk,
        initials,
        first_name,
        prefix,
        last_name,
        birth_date,
        email_address,
        phone_number,
        street_name,
        house_number,
        house_number_addition,
        postal_code,
        city,
        gp_code,
        insurance_code,
        policy_number,
        personal_identification_number,
        first_registration_date,
        cluster_size,
        source_patient_ids
    from {{ ref('int_patient_golden_record') }}

),

singletons as (

    -- patients without duplicates

    select
        patient_id as cluster_id,
        patient_id as master_patient_id,
        {{ dbt_utils.generate_surrogate_key(['patient_id']) }} as patient_sk,
        initials,
        first_name,
        prefix,
        last_name,
        birth_date,
        email_address,
        phone_number_normalized as phone_number,
        street_name,
        house_number_clean AS house_number,
        house_number_addition_correct AS house_number_addition,
        postal_code,
        city,
        gp_code,
        insurance_code,
        policy_number,
        personal_identification_number,
        registration_date AS first_registration_date,
        1 as cluster_size,
        array[patient_id] as source_patient_ids
    from {{ ref('int_patient_prepared') }} p

    where not exists (

        select 1
        from {{ ref('int_patient_clusters') }} c
        where c.patient_id = p.patient_id

    )

)

select 
        patient_sk,
        cluster_id,
        master_patient_id,
        initials,
        first_name,
        prefix,
        last_name,
        birth_date,
        email_address,
        phone_number,
        street_name,
        house_number,
        house_number_addition,
        postal_code,
        city,
        gp_code,
        insurance_code,
        policy_number,
        personal_identification_number,
        first_registration_date,
        cluster_size,
        source_patient_ids,
case
    when cluster_size > 1 then true
    else false
end as is_deduplicated
from golden_records

union all

select 
        patient_sk,
        cluster_id,
        master_patient_id,
        initials,
        first_name,
        prefix,
        last_name,
        birth_date,
        email_address,
        phone_number,
        street_name,
        house_number::TEXT,
        house_number_addition,
        postal_code,
        city,
        gp_code,
        insurance_code,
        policy_number,
        personal_identification_number,
        first_registration_date,
        cluster_size,
        source_patient_ids,

case
    when cluster_size > 1 then true
    else false
end as is_deduplicated
from singletons
