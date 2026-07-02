
select
    patient_id_1,
    patient_id_2,

    case
        when birth_date_1 = birth_date_2
            and birth_date_1 is not null
        then 40
        else 0
    end as score_birth_date,

    case
        when last_name_1 = last_name_2
            and last_name_1 is not null
        then 25
        else 0
    end as score_last_name,

    case
        when first_name_1 = first_name_2
            and first_name_1 is not null
        then 20
        else 0
    end as score_first_name,

    case
        when initials_1 = initials_2
            and initials_1 is not null
        then 10
        else 0
    end as score_initials,

    case
        when postal_code_1 = postal_code_2
            and postal_code_1 is not null
        then 5
        else 0
    end as score_postal_code,

    (
        case
            when birth_date_1 = birth_date_2
                and birth_date_1 is not null
            then 40
            else 0
        end
        +
        case
            when last_name_1 = last_name_2
                and last_name_1 is not null
            then 25
            else 0
        end
        +
        case
            when first_name_1 = first_name_2
                and first_name_1 is not null
            then 20
            else 0
        end
        +
        case
            when initials_1 = initials_2
                and initials_1 is not null
            then 10
            else 0
        end
        +
        case
            when postal_code_1 = postal_code_2
                and postal_code_1 is not null
            then 5
            else 0
        end
    ) as match_score

from {{ ref('int_patient_match_candidates') }}
