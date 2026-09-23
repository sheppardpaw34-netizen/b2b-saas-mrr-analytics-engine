with subscription_periods as (
    select * from {{ref('int_subscription_periods')}}
),

date_spine as (
    select cast(range as date) as date_month
    from range(
        (select date_trunc('month', min(valid_from)) from {{ ref('int_subscription_periods') }}),
        date '2027-01-01',
        interval 1 month
    )


),

subscription_months as (
    select 
        {{ dbt_utils.generate_surrogate_key(['p.subscription_id','d.date_month']) }} as subscription_month_id,
        d.date_month,
        p.subscription_id,
        p.customer_id,
        p.plan_price_id,
        p.mrr,
        p.mrr_movement_type,

        case
            when p.valid_from <= (d.date_month + interval 1 month - interval 1 day)
            and (p.valid_to > d.date_month or p.valid_to is null)
            then true
            else false
        end as is_active_month
    from date_spine d
    inner join subscription_periods p
    on p.valid_from <= (d.date_month + interval 1 month - interval 1 day)
    and ( p.valid_to >= d.date_month or p.valid_to is null)

)

select * from subscription_months
