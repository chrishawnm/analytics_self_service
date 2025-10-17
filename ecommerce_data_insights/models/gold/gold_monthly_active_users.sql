select date_trunc('month', event_date) AS month_start,
       count(distinct user_id) as monthly_active_users
from {{ ref('silver_user_events') }}
group by month_start
order by month_start