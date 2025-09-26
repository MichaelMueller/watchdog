from pydantic import BaseModel

class UvicornConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 21019
    reload: bool = False
    log_level: str = "info"
    workers: int = 1
