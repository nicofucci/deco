from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

import os

@router.post("/login")
def login(payload: LoginRequest):
    # Unify credentials to match .env
    valid_pass = os.getenv("DECO_ADMIN_MASTER_KEY", "admin123")
    
    if payload.username == "Deco" and (payload.password == "deco-security-231908" or payload.password == valid_pass):
        return {"token": valid_pass, "user": "Deco"}
    
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
