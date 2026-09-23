import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set!")

def purge_everything():
    print("Step 1: Canceling all active subscriptions...")
    sub_count = 0
    for sub in stripe.Subscription.list(limit=100).auto_paging_iter():
        print(f"Canceling subscription: {sub.id}")
        stripe.Subscription.cancel(sub.id)
        sub_count += 1
    print(f"Canceled {sub_count} subscriptions.\n")

    print("Step 2: Deleting all customer records...")
    cust_count = 0
    for customer in stripe.Customer.list(limit=100).auto_paging_iter():
        print(f"Deleting customer: {customer.id} ({getattr(customer, 'email', 'No email')})")
        stripe.Customer.delete(customer.id)
        cust_count += 1

    print(f"\nPurge complete! Total customers deleted: {cust_count}")

if __name__ == "__main__":
    purge_everything()