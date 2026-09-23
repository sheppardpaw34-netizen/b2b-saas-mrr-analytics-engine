with subscription_months as (
    select * from {{ref('int_subscription_months')}}
),

customer_cohort as (
    select 
        customer_id,
        min(date_month) as cohort_month
        from subscription_months
        where is_active_month = 'true'
        group by customer_id
),

cohort_retention as (
    select 
        c.cohort_month,
        m.date_month,
        (date_part('year', m.date_month) - date_part('year', c.cohort_month)) * 12 +
        (date_part('month', m.date_month) - date_part('month', c.cohort_month)) as month_number,
        count(distinct m.customer_id) as active_customers,
        sum(m.mrr) as cohort_mrr
    from subscription_months m
    inner join customer_cohort c
    on m.customer_id = c.customer_id
    where m.is_active_month = true
    group by c.cohort_month, m.date_month
)

select * from cohort_retention