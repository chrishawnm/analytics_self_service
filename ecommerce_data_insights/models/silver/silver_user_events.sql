select
    event_id,
    user_id,
    session_id,
    event_type,
    strptime(event_timestamp, '%m/%d/%y %H:%M:%S')::date as event_date,
    page,
    revenue,
    session_duration,
    case when event_type = 'purchase' then 1 else 0 end as is_purchase
from {{ ref('bronze_data_ingest') }}