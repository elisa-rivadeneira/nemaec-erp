"""
Security Headers para producción
"""
from typing import Dict

class SecurityHeaders:
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Headers de seguridad para producción
        """
        return {
            # Prevenir ataques XSS
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",

            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",

            # Content Security Policy básica
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",

            # Prevenir información sensible
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",

            # Server info
            "Server": "NEMAEC-ERP/1.0"
        }