from pydantic_settings import BaseSettings, SettingsConfigDict

from watchdog.data.oidc_config import OidcConfig

from .uvicorn_config import UvicornConfig

class WebAppConfig(BaseSettings, UvicornConfig):
    oidc: OidcConfig    
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="WATCHDOG_", env_nested_delimiter="__")