from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from app.services.redis_bus import JarvisRedisBus
from app.auth.jwt_auth import JarvisAuth, RBACManager

# Inicializar servicios de autenticación
redis_bus = JarvisRedisBus()
auth_system = JarvisAuth(redis_bus)
rbac_manager = RBACManager()

# Seguridad
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency para verificar token JWT."""
    token = credentials.credentials
    payload = auth_system.verify_token(token, "access")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return payload

def require_permission(permission: str):
    """Dependency factory para verificar permisos."""
    async def checker(user: Dict = Depends(get_current_user)):
        role = user.get("role", "viewer")
        if not rbac_manager.has_permission(role, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Rol '{role}' no tiene permiso '{permission}'"
            )
        return user
    return checker
