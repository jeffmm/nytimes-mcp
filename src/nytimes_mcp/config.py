from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for NYT MCP Server."""

    model_config = SettingsConfigDict(env_file=".env")

    nyt_api_key: str
    nyt_api_base_url: str = "https://api.nytimes.com/svc"
    # NYT allows 5 requests per minute, and 500 total requests per day.
    nyt_rate_limit_seconds: int = 12


settings = Settings.model_validate({})
