
with customers as (

    select *
    from {{ ref('int_patient_prepared') }}

),

candidate_pairs as (

    select

        c1.patient_id as patient_id_1,
        c2.patient_id as patient_id_2,

        c1.first_name as first_name_1,
        c2.first_name as first_name_2,

        c1.initials as initials_1,
        c2.initials as initials_2,

        c1.last_name as last_name_1,
        c2.last_name as last_name_2,

        c1.birth_date as birth_date_1,
        c2.birth_date as birth_date_2,

        c1.postal_code as postal_code_1,
        c2.postal_code as postal_code_2,

        c1.street_name as street_name_1,
        c2.street_name as street_name_2,

        c1.house_number_clean as house_number_1,
        c2.house_number_clean as house_number_2

    from customers c1

    inner join customers c2
        on c1.patient_id < c2.patient_id

    where

        (
            c1.birth_date = c2.birth_date
            and left(c1.last_name, 1) = left(c2.last_name, 1)
        )

        or

        (
            c1.last_name = c2.last_name
            and c1.postal_code = c2.postal_code
        )

        or

        (
            c1.initials = c2.initials
            and c1.birth_date = c2.birth_date
        )

)

select *
from candidate_pairs