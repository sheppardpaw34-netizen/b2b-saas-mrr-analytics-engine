with source as (
    select * from {{ source('stripe', 'raw_stripe_subscriptions') }}
),

renamed as (
    select 
        id as subscription_id,
        customer as customer_id,
        status as customer_status,
        items.data[1].price.id as plan_price_id,
        cast(items.data[1].price.unit_amount as numeric) / 100.0 as plan_unit_amount,
        items.data[1].price.recurring.interval as plan_interval,
        to_timestamp(coalesce(start_date, created)) as subscription_started_at,
        to_timestamp(canceled_at) as subscription_canceled_at,
        to_timestamp(created) as created_at
    from source 
)

select * from renamed