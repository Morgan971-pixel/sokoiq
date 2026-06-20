from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sokoiq:sokoiq@localhost:5432/sokoiq"
    anthropic_api_key: str = ""

    model_config = {"env_file": str(_ENV_FILE)}


settings = Settings()
