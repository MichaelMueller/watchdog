from typing import Literal, Optional
from pydantic import BaseModel

from .descriptor import Descriptor
from .watchdog import Watchdog
from .bool_condition import BoolCondition

class WatchdogDescriptor( Descriptor[Watchdog] ):
    type:Literal["watchdog_descriptor"] = "watchdog_descriptor"

    name: Optional[BoolCondition] = None
    
    def equals(self, other:Watchdog):
        return super().equals(other)