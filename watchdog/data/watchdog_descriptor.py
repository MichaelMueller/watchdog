from typing import Literal, Optional
from pydantic import BaseModel

from .descriptor import Descriptor
from .watchdog import Watchdog
from .bool_condition import BoolCondition

class WatchdogDescriptor( Descriptor ):
    type:Literal["watchdog_descriptor"] = "watchdog_descriptor"

    name: Optional[BoolCondition] = None
    enabled: Optional[BoolCondition] = None
    address: Optional[BoolCondition] = None
    port: Optional[BoolCondition] = None
    test_method: Optional[BoolCondition] = None
    