import os
import sys
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SmartDE Double Entry Service"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smart_accounting"
    SPRING_BOOT_MASTER_DATA_GRPC: str = "localhost:9090"
    GEMINI_API_KEY: str = "KEY"

    class Config: env_file = ".env"

settings = Settings()

if "pytest" in sys.modules or os.environ.get("TESTING") == "true":
    settings.DATABASE_URL = "sqlite:///./test.db"

