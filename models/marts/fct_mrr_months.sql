with subscription_months as (
    select * from {{ ref('int_subscription_months') }}
)

select
    subscription_month_id,
    date_month,
    customer_id,
    subscription_id,
    plan_price_id,
    mrr as monthly_mrr,
    is_active_month
from subscription_months
where is_active_month = true