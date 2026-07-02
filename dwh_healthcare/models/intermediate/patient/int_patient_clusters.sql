
with recursive edges as (

    select
        patient_id_1 as patient_id,
        patient_id_2 as connected_patient_id
    from {{ ref('int_patient_match_scores') }}
    where match_score >= 80

    union

    select
        patient_id_2 as patient_id,
        patient_id_1 as connected_patient_id
    from {{ ref('int_patient_match_scores') }}
    where match_score >= 80

),

clusters as (

    -- starting nodes
    select
        patient_id,
        patient_id as cluster_id
    from (
        select patient_id from edges
        union
        select connected_patient_id from edges
    ) n

    union

    -- recursive step
    select
        e.connected_patient_id,
        c.cluster_id
    from clusters c
    join edges e
        on c.patient_id = e.patient_id

)

select
    patient_id,
    min(cluster_id) as cluster_id
from clusters
group by patient_id
