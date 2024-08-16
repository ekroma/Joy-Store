from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:8000"
    BROKER_URL: str
    MEDIA_ROOT: str
    MEDIA_DIR: str = "media"
    DATABASE_URL_MONGODB: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    BASE_DOMAIN: str = "localhost:8000"
    # GOOGLE_CLIENT_ID: str
    # GOOGLE_CLIENT_SECRET: str
    ENV: str

# settings = Settings(_env_file='/home/emir/Desktop/PROJECT/Online_store/online_store/.env') # type: ignore
# settings = Settings(_env_file='C:/Users/evelb/code/project_git/online_store/.env') # type: ignore
settings = Settings(_env_file='.env')  # type: ignore
print(settings)