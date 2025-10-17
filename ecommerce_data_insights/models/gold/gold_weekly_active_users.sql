select date_trunc('week', event_date) AS week_start,
       count(distinct user_id) as weekly_active_users
from {{ ref('silver_user_events') }}
group by week_start
order by week_start