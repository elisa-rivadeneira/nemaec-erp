"""
Sistema de autenticación con JWT para NEMAEC ERP
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

# Configuración de seguridad
SECRET_KEY = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashear contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtener usuario actual desde el token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Por ahora retornamos un usuario simple
    # TODO: Buscar en base de datos
    return {"username": username, "email": f"{username}@nemaec.gob.pe"}

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Verificar que el usuario esté activo"""
    # TODO: Verificar en BD si el usuario está activo
    return current_user

# Usuario admin por defecto para desarrollo
DEFAULT_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@nemaec.gob.pe",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "is_superuser": True
    },
    "monitor": {
        "username": "monitor",
        "email": "monitor@nemaec.gob.pe",
        "hashed_password": get_password_hash("monitor123"),
        "is_active": True,
        "is_superuser": False
    }
}