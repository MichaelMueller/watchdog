from typing import Literal, Optional, Any
from pydantic import BaseModel

from .bool_condition import BoolCondition

class Equals(BoolCondition):
    type:Literal["equals"] = "equals"
    value: Any
    
    def evaluate(self, other: Any) -> bool:
        return self.value == other