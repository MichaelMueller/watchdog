from typing import Literal
from pydantic import BaseModel

class Watchdog(BaseModel):
    name: str
    enabled: bool = True
    address: str
    port: int
    test_method:Literal["ping", "tcp", "http", "https"] = "ping"
