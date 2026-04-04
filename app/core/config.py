from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""



    database_url: str 
    jwt_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    environment: str





    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )



settings = Settings()