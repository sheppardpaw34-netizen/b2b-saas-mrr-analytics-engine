with source as (
    select * from {{ source('stripe', 'raw_stripe_customers')}}
),

renamed as (
    select 
        id as customer_id,
        email as customer_email,
        name as customer_name,
        currency,
        delinquent as is_delinquent,
        metadata.segment as customer_segement,
        metadata.acquisition_channel as acquisition_channel,
        to_timestamp(created) as created_at
    from source

)

select * from renamed