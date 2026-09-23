with mrr_movements as (
    select * from {{ ref('int_subscription_mrr_movements') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['subscription_id', 'created_at']) }} as mrr_movement_id,
    subscription_id,
    customer_id,
    plan_price_id,
    customer_status,
    previous_mrr,
    current_mrr,
    mrr_change,
    mrr_movement_type,
    created_at as movement_at,
    subscription_started_at,
    subscription_canceled_at
from mrr_movements
where mrr_movement_type != 'no_change'