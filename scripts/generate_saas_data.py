import os
import random
import time
from datetime import datetime, timedelta
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set!")

PLANS = [
    {"name": "Starter Monthly", "amount": 2900, "interval": "month"},
    {"name": "Starter Yearly", "amount": 29000, "interval": "year"},
    {"name": "Pro Monthly", "amount": 9900, "interval": "month"},
    {"name": "Pro Yearly", "amount": 99000, "interval": "year"},
    {"name": "Enterprise Monthly", "amount": 29900, "interval": "month"},
    {"name": "Enterprise Yearly", "amount": 299000, "interval": "year"},
]

def get_random_historical_timestamp(start_year=2023, end_offset_days=60):
    """Generates a random epoch timestamp between start_year-01-01 and (today - offset)."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now() - timedelta(days=end_offset_days)
    if end_date <= start_date:
        end_date = datetime.now()
    delta_seconds = int((end_date - start_date).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    random_date = start_date + timedelta(seconds=random_seconds)
    return int(time.mktime(random_date.timetuple()))

def setup_base_products_and_coupons():
    print("Setting up SaaS products, prices, and coupons in Stripe...")
    prices = []
    for plan in PLANS:
        product = stripe.Product.create(name=plan["name"])
        price = stripe.Price.create(
            unit_amount=plan["amount"],
            currency="usd",
            recurring={"interval": plan["interval"]},
            product=product.id,
        )
        prices.append({
            "id": price.id, 
            "interval": plan["interval"], 
            "amount": plan["amount"],
            "name": plan["name"]
        })

    coupon_10 = stripe.Coupon.create(percent_off=10, duration="repeating", duration_in_months=3, name="SMB_10_OFF")
    coupon_20 = stripe.Coupon.create(percent_off=20, duration="once", name="PROMO_20_OFF")
    
    return prices, [coupon_10.id, coupon_20.id]

def generate_realistic_saas_dataset(total_customers=300):
    prices, coupons = setup_base_products_and_coupons()
    
    print(f"\nSeeding {total_customers} production-grade B2B SaaS lifecycle journeys into Stripe API (2023–2026)...")

    for i in range(1, total_customers + 1):
        company_name = f"Company_{i:03d} Inc"
        email = f"billing@company_{i:03d}.com"
        
        # 1. Backdate Customer Signup Timestamp (2023 to ~60 days ago)
        signup_ts = get_random_historical_timestamp(start_year=2023, end_offset_days=60)

        customer = stripe.Customer.create(
            email=email,
            name=company_name,
            source="tok_visa",
            metadata={
                "segment": random.choice(["SMB", "Mid-Market", "Enterprise"]),
                "acquisition_channel": random.choice(["Inbound", "Outbound SDR", "Organic Search", "Paid Ads"]),
            }
        )

        chosen_price = random.choice(prices)
        applied_coupon = random.choice(coupons) if random.random() < 0.25 else None

        # 2. SUBSCRIPTION CREATION (Backdated via backdate_start_date)
        sub_params = {
            "customer": customer.id,
            "items": [{"price": chosen_price["id"]}],
            "backdate_start_date": signup_ts,
            "proration_behavior": "create_prorations",
        }
        if applied_coupon:
            sub_params["discounts"] = [{"coupon": applied_coupon}]

        subscription = stripe.Subscription.create(**sub_params)

        # Finalize initial backdated invoice
        if getattr(subscription, "latest_invoice", None):
            try:
                inv_id = subscription.latest_invoice
                if isinstance(inv_id, dict):
                    inv_id = inv_id.get("id")
                stripe.Invoice.pay(inv_id)
            except Exception:
                pass

        # 3. REAL-WORLD LIFECYCLE MUTATIONS (Expansions, Contractions, Churn)
        roll = random.random()
        
        # SCENARIO A: Mid-Cycle Expansion/Contraction (30% probability)
        if roll < 0.30:
            target_price = random.choice([p for p in prices if p["id"] != chosen_price["id"]])
            try:
                subscription = stripe.Subscription.modify(
                    subscription.id,
                    items=[{
                        "id": subscription["items"]["data"][0]["id"],
                        "price": target_price["id"],
                    }],
                    proration_behavior="always_invoice",
                )
            except Exception:
                pass

        # SCENARIO B: Churn / Cancellation (20% probability)
        elif roll < 0.50:
            try:
                stripe.Subscription.cancel(subscription.id, invoice_now=True)
            except Exception:
                pass

        if i % 25 == 0 or i == total_customers:
            print(f"Progress: {i}/{total_customers} customer lifecycle journeys synced to Stripe API...")

    print("\nProduction-grade dataset successfully generated directly inside Stripe!")

if __name__ == "__main__":
    generate_realistic_saas_dataset(total_customers=300)