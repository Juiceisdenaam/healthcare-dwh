
{{
    config(
        materialized='table',
        alias='dim_date'
    )
}}

with date_spine as (
    select
        generate_series(
            date '1930-01-01',
            date '2100-12-31',
            interval '1 day'
        )::date as calendar_date
)

select
    to_char(calendar_date, 'YYYYMMDD')::int as dim_date_sk,
    calendar_date,

    extract(day from calendar_date) as day_of_month,
    extract(doy from calendar_date) as day_of_year,
    extract(isodow from calendar_date) as day_of_week_iso,

    to_char(calendar_date, 'Dy') as day_name_short,
    to_char(calendar_date, 'FMDay') as day_name,

    extract(week from calendar_date) as iso_week_of_year,
    extract(month from calendar_date) as month_number,

    to_char(calendar_date, 'Mon') as month_name_short,
    to_char(calendar_date, 'FMMonth') as month_name,

    extract(quarter from calendar_date) as quarter_number,
    extract(year from calendar_date) as year_number,

    case when extract(isodow from calendar_date) in (6, 7) then true else false end as is_weekend,

    date_trunc('week', calendar_date)::date as week_start_date,
    (date_trunc('week', calendar_date) + interval '6 day')::date as week_end_date,

    date_trunc('month', calendar_date)::date as month_start_date,
    (date_trunc('month', calendar_date) + interval '1 month - 1 day')::date as month_end_date,

    date_trunc('quarter', calendar_date)::date as quarter_start_date,
    (date_trunc('quarter', calendar_date) + interval '3 month - 1 day')::date as quarter_end_date,

    date_trunc('year', calendar_date)::date as year_start_date,
    (date_trunc('year', calendar_date) + interval '1 year - 1 day')::date as year_end_date,

    extract(year from calendar_date)::int * 100 + extract(week from calendar_date)::int as year_week_number,
    extract(year from calendar_date)::int * 100 + extract(month from calendar_date)::int as year_month_number,

    extract(year from calendar_date)::int || ' Q' || extract(quarter from calendar_date)::int as year_quarter_text

from date_spine
