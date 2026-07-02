
with cluster_members as (

    select *
    from {{ ref('int_patient_cluster_members') }}

)

select

    cluster_id,
    max(patient_id) filter (where survivorship_rank = 1) as patient_id,
    -- names
    {{ preferred_source('initials') }} as initials,
    {{ preferred_source('first_name') }} as first_name,
    {{ preferred_source('prefix') }} as prefix,
    {{ preferred_source('last_name') }} as last_name,

    -- demographics
    {{ oldest_non_null('birth_date') }} as birth_date,

    -- contact details
    {{ newest_non_null('email_address') }} as email_address,
    {{ newest_non_null('phone_number_normalized') }} as phone_number,

    -- address
    max(street_name) filter (where survivorship_rank = 1) as street_name,
    max(house_number) filter (where survivorship_rank = 1) as house_number,
    max(house_number_addition) filter (where survivorship_rank = 1) as house_number_addition,
    max(postal_code) filter (where survivorship_rank = 1) as postal_code,
    max(city) filter (where survivorship_rank = 1) as city,

    {{ preferred_source('gp_code') }} as gp_code,
    {{ preferred_source('insurance_code') }} as insurance_code,
    {{ preferred_source('policy_number') }} as policy_number,
    {{ preferred_source('personal_identification_number') }} as personal_identification_number,

    -- dates
    min(registration_date) as first_registration_date,

    -- lineage/debugging
    count(*) as cluster_size,
    array_agg(patient_id order by patient_id) as source_patient_ids

from cluster_members
group by cluster_id
