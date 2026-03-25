import sys

from pydantic_settings import BaseSettings

_INSECURE_DEFAULT_KEY = "supersecretkey123changeme"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Piping QA/QC System"
    DATABASE_URL: str = "postgresql://piping_user:piping_pass@db:5432/piping_qc"
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    # Set ENVIRONMENT=production to enforce stricter security checks at startup.
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()

if settings.SECRET_KEY == _INSECURE_DEFAULT_KEY:
    msg = (
        "CRITICAL: SECRET_KEY is set to the insecure default value. "
        "Set the SECRET_KEY environment variable to a strong, random secret."
    )
    if settings.ENVIRONMENT.lower() == "production":
        raise RuntimeError(msg)
    print(msg, file=sys.stderr)
