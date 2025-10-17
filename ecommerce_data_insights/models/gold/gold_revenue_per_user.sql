select event_date,
 sum(revenue) * 1.0 / count(distinct user_id) as revenue_per_user
from {{ ref('silver_user_events') }}
group by event_date
order by event_date