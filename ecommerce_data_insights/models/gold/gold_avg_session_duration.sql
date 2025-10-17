select event_date,
avg(session_duration) as avg_session_duration
from {{ ref('silver_user_events') }}
group by event_date
order by event_date