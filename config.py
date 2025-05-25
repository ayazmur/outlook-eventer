from pydantic_settings import BaseSettings  # Изменено здесь!

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OUTLOOK_SERVICE_URL: str = "http://localhost:8000"  # Мок Outlook API

    class Config:
        env_file = ".env"

config = Settings()