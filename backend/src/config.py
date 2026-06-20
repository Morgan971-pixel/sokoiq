from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sokoiq:sokoiq@localhost:5432/sokoiq"
    anthropic_api_key: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
