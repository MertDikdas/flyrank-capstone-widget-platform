from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"

    geo_provider_a_url: str = ""
    geo_provider_b_url: str = ""

    notification_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()