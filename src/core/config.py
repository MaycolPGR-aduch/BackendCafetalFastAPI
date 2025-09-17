from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    TZ: str = "America/Lima"

    class Config:
        env_file = ".env"

settings = Settings()