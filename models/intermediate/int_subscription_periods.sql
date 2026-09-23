with mrr_movements as (
    select * from {{ref('int_subscription_mrr_movements')}}
),

subscription_periods as (
    select 
        subscription_id,
        customer_id,
        plan_price_id,
        current_mrr as mrr,
        mrr_movement_type,
        created_at as valid_from,
        lead(created_at) over (
            partition by subscription_id
            order by created_at
        ) as valid_to,

        case
            when lead(created_at) over (partition by subscription_id order by created_at) is null
                and customer_status = 'active'
            then true
            else false
        end as is_current_period
    from mrr_movements
)

select * from subscription_periods