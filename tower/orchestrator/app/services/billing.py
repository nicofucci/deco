import uuid
from datetime import datetime, timedelta

class BillingService:
    """
    Mock Billing Service simulating Stripe interactions.
    """
    
    PLANS = {
        "starter": {
            "name": "Starter",
            "price": 4900, # cents
            "currency": "usd",
            "features": ["basic_scan", "dashboard"]
        },
        "pro": {
            "name": "Pro",
            "price": 19900,
            "currency": "usd",
            "features": ["basic_scan", "dashboard", "ai_engine", "reports", "priority_support"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 0, # Custom
            "currency": "usd",
            "features": ["all"]
        }
    }

    def create_customer(self, email: str, name: str) -> str:
        # Mock Stripe Customer ID
        return f"cus_{uuid.uuid4().hex[:16]}"

    def create_subscription(self, customer_id: str, plan_id: str):
        if plan_id not in self.PLANS:
            raise ValueError("Invalid plan ID")
            
        # Mock Stripe Subscription
        return {
            "id": f"sub_{uuid.uuid4().hex[:16]}",
            "customer": customer_id,
            "plan": self.PLANS[plan_id],
            "status": "active",
            "current_period_end": datetime.now() + timedelta(days=30)
        }

    def cancel_subscription(self, subscription_id: str):
        return {"status": "canceled"}

    def get_portal_url(self, customer_id: str) -> str:
        # Mock Portal URL
        return "https://billing.stripe.com/p/session/test_123"
