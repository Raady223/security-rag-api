from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (or a .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    gemini_api_key: str = ""  # not needed until step 2
    chat_model: str = "gemini-3.5-flash-lite"
    embedding_model: str = "gemini-embedding-2"
    embedding_dim: int = 768
    top_k: int = 5
    # If even the closest chunk is farther than this, we answer "not found"
    # without calling the LLM. Calibrated on our data; see the README.
    max_distance: float = 0.45


settings = Settings()
