"""
🔐 SECURITY CORE
Manejo de autenticación, autorización y encriptación.
JWT tokens, password hashing, y utilidades de seguridad.
"""
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# 🔒 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar contraseña plana contra hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de contraseña almacenado

    Returns:
        bool: True si la contraseña coincide
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generar hash de contraseña.

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash de la contraseña
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crear token JWT de acceso.

    Args:
        subject: Identificador del usuario (user_id)
        expires_delta: Tiempo de expiración personalizado

    Returns:
        str: Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verificar y decodificar token JWT.

    Args:
        token: Token JWT a verificar

    Returns:
        Optional[str]: Subject del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def generate_api_key() -> str:
    """
    Generar API key para integraciones externas.

    Returns:
        str: API key único
    """
    import secrets
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> dict[str, Any]:
    """
    Validar fortaleza de contraseña según políticas institucionales.

    Args:
        password: Contraseña a validar

    Returns:
        dict: Resultado de validación con detalles
    """
    result = {
        "is_valid": False,
        "score": 0,
        "errors": [],
        "suggestions": []
    }

    # Políticas de seguridad NEMAEC
    if len(password) < 8:
        result["errors"].append("La contraseña debe tener al menos 8 caracteres")
    else:
        result["score"] += 1

    if not any(c.isupper() for c in password):
        result["errors"].append("Debe contener al menos una mayúscula")
    else:
        result["score"] += 1

    if not any(c.islower() for c in password):
        result["errors"].append("Debe contener al menos una minúscula")
    else:
        result["score"] += 1

    if not any(c.isdigit() for c in password):
        result["errors"].append("Debe contener al menos un número")
    else:
        result["score"] += 1

    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        result["errors"].append("Debe contener al menos un carácter especial")
    else:
        result["score"] += 1

    # Contraseñas comunes prohibidas
    common_passwords = [
        "password", "123456", "qwerty", "admin", "nemaec", "policia"
    ]
    if password.lower() in common_passwords:
        result["errors"].append("Contraseña muy común, elige una más segura")

    result["is_valid"] = len(result["errors"]) == 0

    # Sugerencias según score
    if result["score"] < 3:
        result["suggestions"].append("Usa una combinación de mayúsculas, minúsculas y números")
    if result["score"] < 4:
        result["suggestions"].append("Agrega caracteres especiales para mayor seguridad")
    if len(password) < 12:
        result["suggestions"].append("Considera usar al menos 12 caracteres")

    return result


class SecurityHeaders:
    """
    Headers de seguridad recomendados para producción.
    """

    @staticmethod
    def get_security_headers() -> dict[str, str]:
        """
        Obtener headers de seguridad estándar.

        Returns:
            dict: Headers de seguridad
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=()"
            )
        }


def sanitize_filename(filename: str) -> str:
    """
    Sanitizar nombre de archivo para prevenir path traversal.

    Args:
        filename: Nombre de archivo original

    Returns:
        str: Nombre de archivo sanitizado
    """
    import re
    import os

    # Remover path separators y caracteres peligrosos
    filename = os.path.basename(filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remover caracteres de control
    filename = ''.join(char for char in filename if ord(char) >= 32)

    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename or "untitled"