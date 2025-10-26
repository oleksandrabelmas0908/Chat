from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int


    class Config:
        env_file = ".env"

    
settings = Settings()