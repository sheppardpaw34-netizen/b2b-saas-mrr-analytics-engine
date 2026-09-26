with source as (
    select * from {{ source('raw_stripe', 'raw_stripe_subscriptions')}}
),

renamed as (
    select 
        id as subscription_id,
        customer as customer_id,
        plan.id as plan_id,
        plan.interval as plan_interval,
        plan.interval_count as plan_interval_count,
        plan.amount / 100.0 as plan_unit_price_usd,
        quantity,
        status as subscription_status,
        case 
            when status in ('active', 'trialing') then true
            else false
        end as is_active,
        to_timestamp (cast(created as bigint)) as created_at,
        to_timestamp (cast(billing_cycle_anchor as bigint)) as billing_cycle_anchor_at,
        to_timestamp(cast(cancel_at as bigint)) as scheduled_cancel_at,
        to_timestamp(cast(canceled_at as bigint)) as canceled_at,
        to_timestamp(cast(ended_at as bigint)) as ended_at,
        to_timestamp(cast(trial_start as bigint)) as trial_started_at,
        to_timestamp(cast(trial_end as bigint)) as trail_ended_at,
        cancel_at_period_end as is_schedule_to_cancel
    from source

)

select * from renamed