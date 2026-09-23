with subscriptions as (
    select * from {{ref('stg_stripe__subscriptions')}}
),

mrr_lagged as (
    select 
        subscription_id,
        customer_id,
        customer_status,
        plan_price_id,
        plan_unit_amount as current_mrr,
        subscription_started_at,
        subscription_canceled_at,
        created_at,

        lag(plan_unit_amount, 1, 0.0) over (
            partition by customer_id, subscription_id
            order by created_at
        ) as previous_mrr
    from subscriptions

),

mrr_classified as (
    select 
        subscription_id,
        customer_id,
        customer_status,
        plan_price_id,
        subscription_started_at,
        subscription_canceled_at,
        created_at,
        current_mrr,
        previous_mrr,
        (current_mrr - previous_mrr) as mrr_change,
        case 
            when previous_mrr = 0 and current_mrr >0 then 'new'
            when current_mrr > previous_mrr and previous_mrr > 0 then 'expansion'
            when current_mrr < previous_mrr and current_mrr > 0 then 'contraction'
            when current_mrr = 0 and previous_mrr > 0 then 'churn'
            when previous_mrr = 0 and current_mrr > 0 and customer_status = 'active' then 'reactivation'
            else 'no_change'
        end as mrr_movement_type
    from mrr_lagged

)

select * from mrr_classified