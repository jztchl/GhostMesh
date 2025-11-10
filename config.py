from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    GEMINI_API_KEY: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
