WITH cluster_members as (
    select
        c.cluster_id,
        p.*
    from {{ ref('int_patient_clusters') }} c
    join {{ ref('int_patient_prepared') }} p
        on c.patient_id = p.patient_id
),

scored as (

    select
        *,
            case source_system
            when 'EPD_A' then 1
            when 'EPD_B' then 2
            when 'EPD_C' then 3
            else 99
        end as source_priority,
        (
            case when first_name is not null then 1 else 0 end +
            case when last_name is not null then 1 else 0 end +
            case when birth_date is not null then 1 else 0 end +
            case when email_address is not null then 1 else 0 end +
            case when phone_number is not null then 1 else 0 end +
            case when street_name is not null then 1 else 0 end +
            case when postal_code is not null then 1 else 0 end
        ) as completeness_score

    from cluster_members

)

select
    *,
    row_number() over (
        partition by cluster_id
        order by
            completeness_score desc,
            registration_date desc,
            source_priority asc,
            patient_id desc
    ) as survivorship_rank

from scored


