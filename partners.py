from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class PartnerLogin(BaseModel):
    email: str
    password: str

class PartnerProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str = "partner"

@router.post("/login")
async def partner_login(creds: PartnerLogin):
    # Mock login - accept any credentials for now to allow access
    if "@" in creds.email and len(creds.password) > 0:
        return {"token": "mock_partner_token_123", "user": {"id": "p1", "name": "Partner Demo", "email": creds.email}}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@router.get("/me", response_model=PartnerProfile)
async def get_me():
    return PartnerProfile(id="p1", name="Partner Demo", email="demo@partner.com")

@router.get("/me/clients")
async def get_my_clients():
    return []

@router.get("/me/earnings")
async def get_my_earnings():
    return {"total": 0, "month": 0, "pending": 0}

@router.get("/api-keys")
async def get_api_keys():
    return []
