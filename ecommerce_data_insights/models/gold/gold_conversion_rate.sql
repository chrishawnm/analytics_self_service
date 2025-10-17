with base as (
    select 
        event_date,
        user_id,
        event_type
    from {{ ref('silver_user_events') }}
)

select 
    event_date,
    count(distinct case when event_type = 'purchase' then user_id end) * 1.0 
      / count(distinct user_id) as conversion_rate
from base
group by event_date
order by event_date