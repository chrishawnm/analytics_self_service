{{ config(materialized='table') }}

with recursive date_spine as (
    select date('2020-01-01') as date_day
    union all
    select date_add(date_day, interval 1 day)
    from date_spine
    where date_day < current_date
)
select date_day
from date_spine