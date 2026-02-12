from fastapi import APIRouter, HTTPException
from typing import List
from app.models.tenant import Tenant
import uuid
from datetime import datetime

router = APIRouter()

# Simulación de base de datos en memoria
TENANTS_DB: List[Tenant] = [
    Tenant(
        id="tenant_default",
        name="Global / Internal",
        slug="global",
        contact_email="admin@deco.local",
        status="active",
        scope_whitelist=["*"]
    )
]

@router.get("/", response_model=List[Tenant])
async def list_tenants():
    """Lista todos los clientes registrados."""
    return TENANTS_DB

@router.post("/", response_model=Tenant)
async def create_tenant(tenant: Tenant):
    """Registra un nuevo cliente."""
    if any(t.slug == tenant.slug for t in TENANTS_DB):
        raise HTTPException(status_code=400, detail="Tenant slug already exists")
    
    TENANTS_DB.append(tenant)
    return tenant

@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    tenant = next((t for t in TENANTS_DB if t.id == tenant_id), None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
