from typing import Literal, Optional
from pydantic import BaseModel

from .query import Query

class UpdateWatchdog(Query):
    type:Literal["update_watchdog"] = "update_watchdog"
    name: str
    
    enabled: Optional[bool] = None
    address: Optional[str] = None
    port: Optional[int] = None
    test_method: Optional[Literal["ping", "tcp", "http", "https"]] = None
