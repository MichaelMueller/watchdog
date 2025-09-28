from typing import Literal
from pydantic import BaseModel

from .insert import Insert
from .watchdog import Watchdog

class CreateWatchdog(Insert, Watchdog):
    type:Literal["create_watchdog"] = "create_watchdog"
