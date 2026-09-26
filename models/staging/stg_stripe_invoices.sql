with source as (
    select * from {{ source('raw_stripe','raw_stripe_invoices')}}
),

renamed as (
    select 
        id as invoice_id,
        customer as customer_id,
        number as invoice_number,
        status as invoice_status,
        currency,
        parent.subscription_details as subscription_details,
        billing_reason,
        collection_method,

        coalesce(amount_due, 0) / 100.0 as amount_due_usd,
        coalesce(amount_paid, 0) / 100.0 as amount_paid_usd,
        coalesce(amount_remaining, 0) / 100.0 as amount_remaining_usd,
        coalesce(subtotal, 0) / 100.0 as subtotal_usd,
        coalesce(total, 0) / 100.0 as total_usd,
        coalesce(starting_balance, 0) / 100.0 as starting_balance_usd,
        coalesce(ending_balance, 0) / 100.0 as ending_balance_usd,
        attempted as is_attempted,
        case when status = 'paid' then true else false end as is_paid,
        case when status = 'uncollectible' then true else false end as is_uncollectible,
        case when status = 'void' then true else false end as is_voided,
        to_timestamp(cast(created as bigint)) as created_at,
        to_timestamp(cast(due_date as bigint)) as payment_due_at,
        to_timestamp(cast(effective_at as bigint)) as effective_at,
        to_timestamp(cast(period_start as bigint)) as invoice_period_started_at,
        to_timestamp(cast(period_end as bigint)) as invoice_period_ended_at,

        to_timestamp(cast(status_transitions.finalized_at as bigint)) as finalized_at,
        to_timestamp(cast(status_transitions.marked_uncollectible_at as bigint)) as marked_uncollectible_at,
        to_timestamp(cast(status_transitions.paid_at as bigint)) as paid_at,
        to_timestamp(cast(status_transitions.voided_at as bigint)) as voided_at
    from source


)

select * from renamed