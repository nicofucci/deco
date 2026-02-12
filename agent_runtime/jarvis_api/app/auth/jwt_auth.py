"""
Sistema de Autenticación JWT con Refresh Tokens
Jarvis 3.0
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import secrets

# Configuración
SECRET_KEY = secrets.token_urlsafe(64)  # En producción: variable de entorno
REFRESH_SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    username: str
    role: str
    permissions: list[str] = []

class JarvisAuth:
    """Sistema de autenticación JWT para Jarvis."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crea access token JWT."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any]
    ) -> str:
        """Crea refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        
        # Guardar en Redis para verificación
        token_key = f"refresh_token:{data.get('sub')}"
        self.redis.redis.setex(
            token_key,
            int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
            encoded_jwt
        )
        
        return encoded_jwt
    
    def verify_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica token JWT."""
        try:
            secret = SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY
            payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                return None
            
            # Si es refresh token, verificar en Redis
            if token_type == "refresh":
                username = payload.get("sub")
                stored_token = self.redis.redis.get(f"refresh_token:{username}")
                if not stored_token or stored_token != token:
                    return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None
    
    def revoke_refresh_token(self, username: str):
        """Revoca refresh token de usuario."""
        self.redis.redis.delete(f"refresh_token:{username}")
    
    def hash_password(self, password: str) -> str:
        """Hash de contraseña."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña."""
        return pwd_context.verify(plain_password, hashed_password)


class RBACManager:
    """Role-Based Access Control Manager."""
    
    # Definición de roles y permisos
    ROLES = {
        "admin": {
            "permissions": [
                "read", "write", "delete",
                "execute_agents", "manage_users",
                "access_lab", "configure_system"
            ],
            "description": "Administrador completo del sistema"
        },
        "analyst": {
            "permissions": [
                "read", "write",
                "execute_agents", "access_lab"
            ],
            "description": "Analista de seguridad"
        },
        "viewer": {
            "permissions": ["read"],
            "description": "Solo lectura"
        },
        "api_user": {
            "permissions": ["read", "execute_agents"],
            "description": "Usuario API externo"
        }
    }
    
    def __init__(self):
        pass
    
    def has_permission(self, role: str, permission: str) -> bool:
        """Verifica si un rol tiene un permiso."""
        role_data = self.ROLES.get(role)
        if not role_data:
            return False
        
        return permission in role_data.get("permissions", [])
    
    def get_role_permissions(self, role: str) -> list[str]:
        """Obtiene todos los permisos de un rol."""
        role_data = self.ROLES.get(role)
        if not role_data:
            return []
        
        return role_data.get("permissions", [])
    
    def validate_action(
        self,
        role: str,
        action: str,
        resource: str = None
    ) -> bool:
        """Valida si un rol puede ejecutar una acción."""
        # Mapeo de acciones a permisos
        action_permissions = {
            "chat": "read",
            "rag_upload": "write",
            "rag_query": "read",
            "execute_recon": "execute_agents",
            "execute_exploit": "access_lab",
            "manage_users": "manage_users",
            "configure": "configure_system"
        }
        
        required_permission = action_permissions.get(action)
        if not required_permission:
            return False
        
        return self.has_permission(role, required_permission)


# Middleware para FastAPI
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials,
    auth_manager: JarvisAuth
) -> TokenData:
    """Middleware para verificar token JWT."""
    token = credentials.credentials
    
    payload = auth_manager.verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenData(
        username=payload.get("sub"),
        role=payload.get("role", "viewer"),
        permissions=payload.get("permissions", [])
    )

async def require_permission(
    token_data: TokenData,
    required_permission: str
) -> bool:
    """Verifica que el usuario tenga el permiso requerido."""
    rbac = RBACManager()
    
    if not rbac.has_permission(token_data.role, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso denegado: se requiere '{required_permission}'"
        )
    
    return True
