with source as (
    select * from {{ source('stripe', 'raw_stripe_invoices')}}
),

renamed as (
    select
        id as invoice_id,
        customer as customer_id,
        parent.subscription_details.subscription as subscription_id,
        status as invoice_status,
        currency,
        cast(amount_due as numeric) /100.0 as amount_due,
        cast(amount_paid as numeric) /100.0 as amount_paid,
        cast(amount_remaining as numeric) /100.0 as amount_remaining,
        cast(subtotal as numeric) /100.0 as subtotal_amount,
        cast(total as numeric) /100.0 as total_amount,
        to_timestamp(created) as created_at,
        to_timestamp(status_transitions.paid_at) as paid_at
    from source 
)

select * from renamed