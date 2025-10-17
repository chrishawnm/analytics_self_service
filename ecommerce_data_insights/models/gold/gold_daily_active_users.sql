select event_date,
count(distinct user_id) as daily_active_users
from {{ ref('silver_user_events') }}
group by event_date
order by event_date