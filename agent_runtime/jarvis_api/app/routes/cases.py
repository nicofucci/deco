from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.cases_sql import CaseORM

router = APIRouter()

# --- Pydantic Schemas ---

class CaseCreate(BaseModel):
    title: str
    description: str
    status: str = "open"
    severity: str = "medium"
    client_id: Optional[str] = None
    asset_id: Optional[str] = None

class CaseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    severity: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    client_id: Optional[str] = None
    asset_id: Optional[str] = None

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/", response_model=List[CaseResponse])
async def list_cases(db: Session = Depends(get_db)):
    """Lista todos los casos ordenados por fecha de creación descendente."""
    cases = db.query(CaseORM).order_by(desc(CaseORM.created_at)).all()
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Obtiene detalles de un caso por ID."""
    case = db.query(CaseORM).filter(CaseORM.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/", response_model=CaseResponse)
async def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    """Crea un nuevo caso en la base de datos."""
    new_case = CaseORM(
        id=str(uuid.uuid4()),
        title=case_in.title,
        description=case_in.description,
        status=case_in.status,
        severity=case_in.severity,
        client_id=case_in.client_id,
        asset_id=case_in.asset_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case
