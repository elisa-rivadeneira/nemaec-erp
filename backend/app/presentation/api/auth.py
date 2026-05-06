"""
API de autenticación
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import (
    verify_password, create_access_token, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, DEFAULT_USERS
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login con username y password
    """
    # Buscar usuario en DEFAULT_USERS (temporal)
    user = DEFAULT_USERS.get(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "is_superuser": user.get("is_superuser", False)
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual
    """
    return current_user

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """
    Endpoint de logout (en el cliente se debe eliminar el token)
    """
    return {"message": "Sesión cerrada exitosamente"}