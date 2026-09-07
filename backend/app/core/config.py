from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/tolti.db"
    modal_api_key: str = ""
    modal_app_name: str = ""
    environment: str = "development"


settings = Settings()
