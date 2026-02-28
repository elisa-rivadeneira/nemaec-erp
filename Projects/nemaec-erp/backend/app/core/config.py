"""
🏗️ CORE CONFIGURATION
Configuración centralizada con Pydantic Settings.
Siguiendo principios de 12-factor app.
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación.
    Todas las configuraciones deben ser inyectadas por variables de entorno.
    """

    # 🏷️ Project Information
    PROJECT_NAME: str = Field(
        default="NEMAEC ERP",
        description="Nombre del proyecto"
    )

    PROJECT_DESCRIPTION: str = Field(
        default="Núcleo Ejecutor de Mantenimiento, Acondicionamiento y Equipamiento de Comisarías",
        description="Descripción del proyecto"
    )

    VERSION: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )

    API_PREFIX: str = Field(
        default="/api/v1",
        description="Prefijo para todas las rutas de API"
    )

    # 🌍 Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="Entorno de ejecución: development, staging, production"
    )

    DEBUG: bool = Field(
        default=True,
        description="Activar modo debug (solo development)"
    )

    # 🗄️ Database Configuration
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="URL completa de conexión a PostgreSQL"
    )

    DB_HOST: str = Field(
        default="localhost",
        description="Host de la base de datos"
    )

    DB_PORT: int = Field(
        default=5432,
        description="Puerto de PostgreSQL"
    )

    DB_NAME: str = Field(
        default="nemaec_erp",
        description="Nombre de la base de datos"
    )

    DB_USER: str = Field(
        default="nemaec_user",
        description="Usuario de la base de datos"
    )

    DB_PASSWORD: str = Field(
        default="nemaec_password",
        description="Contraseña de la base de datos"
    )

    # 🔐 Security Configuration
    SECRET_KEY: str = Field(
        default="nemaec-super-secret-key-change-in-production",
        min_length=32,
        description="Clave secreta para JWT y encriptación"
    )

    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo para JWT"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24 horas
        description="Tiempo de expiración del token JWT en minutos"
    )

    # 🌐 CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Orígenes permitidos para CORS"
    )

    # 📦 Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexión a Redis"
    )

    # 📁 File Storage
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Directorio para archivos subidos"
    )

    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamaño máximo de archivo en bytes"
    )

    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[".xlsx", ".xls", ".pdf"],
        description="Extensiones de archivo permitidas"
    )

    # 🚀 Performance
    DB_POOL_SIZE: int = Field(
        default=20,
        description="Tamaño del pool de conexiones de DB"
    )

    DB_MAX_OVERFLOW: int = Field(
        default=0,
        description="Conexiones adicionales permitidas"
    )

    # 📧 External Services (para futuras integraciones)
    EMAIL_SMTP_HOST: Optional[str] = Field(
        default=None,
        description="Servidor SMTP para envío de emails"
    )

    EMAIL_SMTP_PORT: int = Field(
        default=587,
        description="Puerto SMTP"
    )

    # 🔄 Integration with Gestor Documentario
    GESTOR_DOCUMENTARIO_URL: Optional[str] = Field(
        default="http://localhost:8001",
        description="URL del Gestor Documentario existente"
    )

    GESTOR_DOCUMENTARIO_API_KEY: Optional[str] = Field(
        default=None,
        description="API Key para integración con Gestor Documentario"
    )

    # 🗺️ Google Maps Integration
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(
        default=None,
        description="API Key para Google Maps Places API"
    )

    @property
    def database_url(self) -> str:
        """
        Construye la URL de base de datos si no se proporciona una completa.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def is_production(self) -> bool:
        """Verifica si estamos en producción"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Verifica si estamos en desarrollo"""
        return self.ENVIRONMENT.lower() == "development"

    class Config:
        """Configuración de Pydantic Settings"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        # Ejemplo de .env file esperado
        env_example = """
        # 🏷️ Project
        PROJECT_NAME="NEMAEC ERP"
        ENVIRONMENT=development
        DEBUG=true

        # 🗄️ Database
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=nemaec_erp
        DB_USER=nemaec_user
        DB_PASSWORD=nemaec_secure_password

        # 🔐 Security
        SECRET_KEY=your-super-secret-key-here-min-32-chars
        ACCESS_TOKEN_EXPIRE_MINUTES=1440

        # 📦 Redis
        REDIS_URL=redis://localhost:6379/0

        # 🔄 Integration
        GESTOR_DOCUMENTARIO_URL=http://localhost:8001
        GESTOR_DOCUMENTARIO_API_KEY=your-integration-key
        """


# 🌍 Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency para inyectar configuración en FastAPI.

    Usage:
        @app.get("/config")
        def get_config(config: Settings = Depends(get_settings)):
            return {"environment": config.ENVIRONMENT}
    """
    return settings