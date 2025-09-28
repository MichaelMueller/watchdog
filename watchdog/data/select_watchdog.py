from typing import Literal, Optional
from pydantic import BaseModel

from .watchdog import Watchdog
from .select import Select

class SelectWatchdog(Select[Watchdog]):
    type:Literal["select_watchdog"] = "select_watchdog"
    
