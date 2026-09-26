import random
import time
from datetime import datetime, timedelta
import duckdb
import pandas as pd

def get_random_historical_timestamp(start_year=2023, max_days_ago=60):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now() - timedelta(days=max_days_ago)
    delta_seconds = int((end_date - start_date).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    return int(time.mktime((start_date + timedelta(seconds=random_seconds)).timetuple()))

PLANS = [
    {"id": "price_starter_m", "name": "Starter Monthly", "amount": 2900, "interval": "month"},
    {"id": "price_starter_y", "name": "Starter Yearly", "amount": 29000, "interval": "year"},
    {"id": "price_pro_m", "name": "Pro Monthly", "amount": 9900, "interval": "month"},
    {"id": "price_pro_y", "name": "Pro Yearly", "amount": 99000, "interval": "year"},
    {"id": "price_enterprise_m", "name": "Enterprise Monthly", "amount": 29900, "interval": "month"},
    {"id": "price_enterprise_y", "name": "Enterprise Yearly", "amount": 299000, "interval": "year"},
]

def generate_and_load_duckdb(total_customers=300, db_path="dev.duckdb"):
    print(f"Generating {total_customers} backdated B2B SaaS records directly into DuckDB...")
    
    customers = []
    subscriptions = []
    invoices = []

    for i in range(1, total_customers + 1):
        cust_id = f"cus_test_{i:04d}"
        company_name = f"Company_{i:03d} Inc"
        email = f"billing@company_{i:03d}.com"
        
        # 1. Backdated customer creation date (2023 - 2026)
        cust_created = get_random_historical_timestamp(start_year=2023, max_days_ago=120)
        
        customers.append({
            "id": cust_id,
            "name": company_name,
            "email": email,
            "currency": "usd",
            "balance": 0,
            "created": cust_created,
            "delinquent": False,
            "livemode": False,
            "metadata": {
                "segment": random.choice(["SMB", "Mid-Market", "Enterprise"]),
                "acquisition_channel": random.choice(["Inbound", "Outbound SDR", "Organic Search", "Paid Ads"])
            }
        })

        # 2. Subscription starts shortly after customer registration
        sub_id = f"sub_test_{i:04d}"
        sub_created = cust_created + random.randint(86400, 864000) # 1 to 10 days later
        chosen_plan = random.choice(PLANS)
        
        roll = random.random()
        status = "active"
        canceled_at = None
        ended_at = None
        
        if roll < 0.20:
            status = "canceled"
            canceled_at = sub_created + random.randint(2592000, 15552000) # Canceled 1-6 months later
            ended_at = canceled_at

        subscriptions.append({
            "id": sub_id,
            "customer": cust_id,
            "status": status,
            "created": sub_created,
            "billing_cycle_anchor": sub_created,
            "cancel_at": None,
            "canceled_at": canceled_at,
            "ended_at": ended_at,
            "trial_start": None,
            "trial_end": None,
            "cancel_at_period_end": False,
            "quantity": 1,
            "plan": {
                "id": chosen_plan["id"],
                "interval": chosen_plan["interval"],
                "interval_count": 1,
                "amount": chosen_plan["amount"]
            }
        })

        # 3. Synchronized invoice timestamps
        inv_id = f"in_test_{i:04d}"
        invoices.append({
            "id": inv_id,
            "customer": cust_id,
            "number": f"INV-{i:04d}",
            "parent": {"subscription_details": sub_id},
            "status": "paid" if status == "active" else "void",
            "currency": "usd",
            "billing_reason": "subscription_create",
            "collection_method": "charge_automatically",
            "amount_due": chosen_plan["amount"],
            "amount_paid": chosen_plan["amount"] if status == "active" else 0,
            "amount_remaining": 0,
            "subtotal": chosen_plan["amount"],
            "total": chosen_plan["amount"],
            "starting_balance": 0,
            "ending_balance": 0,
            "attempted": True,
            "livemode": False,
            "created": sub_created,
            "due_date": sub_created,
            "effective_at": sub_created,
            "period_start": sub_created,
            "period_end": sub_created + (2592000 if chosen_plan["interval"] == "month" else 31536000),
            "status_transitions": {
                "finalized_at": sub_created,
                "marked_uncollectible_at": None,
                "paid_at": sub_created if status == "active" else None,
                "voided_at": sub_created if status == "canceled" else None
            }
        })

    # Convert Python lists to Pandas DataFrames
    df_cust = pd.DataFrame(customers)
    df_sub = pd.DataFrame(subscriptions)
    df_inv = pd.DataFrame(invoices)

    # Load directly into DuckDB raw schema
    conn = duckdb.connect(db_path)
    conn.execute("create schema if not exists raw;")
    
    conn.execute("drop table if exists raw.raw_stripe_customers;")
    conn.execute("drop table if exists raw.raw_stripe_subscriptions;")
    conn.execute("drop table if exists raw.raw_stripe_invoices;")

    conn.register("df_cust", df_cust)
    conn.register("df_sub", df_sub)
    conn.register("df_inv", df_inv)

    conn.execute("create table raw.raw_stripe_customers as select * from df_cust;")
    conn.execute("create table raw.raw_stripe_subscriptions as select * from df_sub;")
    conn.execute("create table raw.raw_stripe_invoices as select * from df_inv;")

    conn.close()
    print("Database populated successfully with realistic 2023-2026 timelines!")

if __name__ == "__main__":
    generate_and_load_duckdb(total_customers=300)