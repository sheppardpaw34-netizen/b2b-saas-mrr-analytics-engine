with customers as (
    select * from {{ ref('stg_stripe__customers') }}
),

subscription_months as (
    select * from {{ ref('int_subscription_months') }}
),

customer_aggregates as (
    select
        customer_id,
        min(date_month) as first_active_month,
        max(date_month) as last_active_month,
        sum(mrr) as lifetime_mrr_contributed,
        max(mrr) as peak_mrr
    from subscription_months
    where is_active_month = true
    group by customer_id
)

select
    c.customer_id,
    c.customer_email,
    c.customer_name,
    c.currency,
    coalesce(a.first_active_month, cast(c.created_at as date)) as first_active_month,
    a.last_active_month,
    coalesce(a.lifetime_mrr_contributed, 0.0) as lifetime_mrr_contributed,
    coalesce(a.peak_mrr, 0.0) as peak_mrr,
    c.created_at
from customers c
left join customer_aggregates a
    on c.customer_id = a.customer_id