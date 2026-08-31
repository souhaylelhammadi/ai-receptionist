import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")


settings = Settings()