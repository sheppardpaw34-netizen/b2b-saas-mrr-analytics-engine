import os
import duckdb
import pandas as pd
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set!")

def extract_raw_stripe_data():
    print("Extracting pure raw payloads from Stripe API...")

    # 1. RAW CUSTOMERS
    print("Fetching Raw Customers...")
    raw_customers = [
        c.to_dict() 
        for c in stripe.Customer.list(limit=100).auto_paging_iter()
    ]
    df_customers = pd.DataFrame(raw_customers)

    # 2. RAW SUBSCRIPTIONS
    print("Fetching Raw Subscriptions...")
    raw_subs = [
        s.to_dict() 
        for s in stripe.Subscription.list(status="all", limit=100).auto_paging_iter()
    ]
    df_subscriptions = pd.DataFrame(raw_subs)

    # 3. RAW INVOICES
    print("Fetching Raw Invoices...")
    raw_invoices = [
        inv.to_dict() 
        for inv in stripe.Invoice.list(limit=100).auto_paging_iter()
    ]
    df_invoices = pd.DataFrame(raw_invoices)

    # 4. WRITE RAW SCHEMAS TO MOTHERDUCK OR LOCAL DUCKDB
    target_env = os.getenv("DBT_TARGET", "dev").lower()
    
    if target_env == "prod":
        md_token = os.getenv("MOTHERDUCK_TOKEN")
        if not md_token:
            raise ValueError("MOTHERDUCK_TOKEN environment variable is not set!")
        print("\nConnecting to MotherDuck (md:my_mrr_db)...")
        con = duckdb.connect("md:my_mrr_db", config={"motherduck_token": md_token})
    else:
        print("\nWriting raw tables to dev.duckdb...")
        con = duckdb.connect("dev.duckdb")
    
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("CREATE OR REPLACE TABLE raw.raw_stripe_customers AS SELECT * FROM df_customers")
    con.execute("CREATE OR REPLACE TABLE raw.raw_stripe_subscriptions AS SELECT * FROM df_subscriptions")
    con.execute("CREATE OR REPLACE TABLE raw.raw_stripe_invoices AS SELECT * FROM df_invoices")

    print(f"Success! Raw tables written to {target_env} environment with native Stripe API column schemas.")
    con.close()

if __name__ == "__main__":
    extract_raw_stripe_data()