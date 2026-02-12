from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.api.deps import get_db, verify_master_key
from app.models.domain import Client, Subscription
from app.services.billing import BillingService

router = APIRouter()
billing_service = BillingService()

class PlanRead(BaseModel):
    id: str
    name: str
    price: int
    currency: str
    features: List[str]

class SubscribeRequest(BaseModel):
    client_id: str
    plan_id: str

@router.get("/plans", response_model=List[PlanRead])
def list_plans():
    plans = []
    for pid, pdata in billing_service.PLANS.items():
        plans.append({
            "id": pid,
            "name": pdata["name"],
            "price": pdata["price"],
            "currency": pdata["currency"],
            "features": pdata["features"]
        })
    return plans

@router.post("/subscribe")
def subscribe_client(
    payload: SubscribeRequest,
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if subscription exists
    sub = db.query(Subscription).filter(Subscription.client_id == client.id).first()
    
    if not sub:
        # Create initial record
        stripe_cus_id = billing_service.create_customer(client.contact_email, client.name)
        sub = Subscription(
            client_id=client.id,
            stripe_customer_id=stripe_cus_id,
            plan_id="starter" # Default
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

    # Update subscription via service
    try:
        stripe_sub = billing_service.create_subscription(sub.stripe_customer_id, payload.plan_id)
        
        sub.plan_id = payload.plan_id
        sub.status = stripe_sub["status"]
        sub.current_period_end = stripe_sub["current_period_end"]
        
        db.commit()
        db.refresh(sub)
        
        return {"status": "success", "subscription": sub.plan_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portal/{client_id}")
def get_billing_portal(
    client_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    sub = db.query(Subscription).filter(Subscription.client_id == client_id).first()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No billing account found")
        
    url = billing_service.get_portal_url(sub.stripe_customer_id)
    return {"url": url}

@router.get("/status/{client_id}")
def get_subscription_status(
    client_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    sub = db.query(Subscription).filter(Subscription.client_id == client_id).first()
    if not sub:
        return {"plan": "none", "status": "inactive"}
        
    return {
        "plan": sub.plan_id,
        "status": sub.status,
        "expires_at": sub.current_period_end
    }
