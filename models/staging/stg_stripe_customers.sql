with source as (
    select * from {{source('raw_stripe','raw_stripe_customers')}}
),

renamed as (
    select 
        id as customer_id,
        name as customer_name,
        email as customer_email,
        currency,
        balance / 100.0 as balance_amount,
        to_timestamp(cast(created as bigint)) as created_at,
        delinquent as is_delinquent,
        livemode as is_livemode,
        metadata.acquisition_channel as acquisition_channel,
        metadata.segment as customer_segment
    from source
)

select * from renamed