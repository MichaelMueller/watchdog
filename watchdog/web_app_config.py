from pydantic_settings import BaseSettings, SettingsConfigDict

class WebAppConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 21019
    reload: bool = False
    log_level: str = "info"
    workers: int = 1

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="WATCHDOG_")