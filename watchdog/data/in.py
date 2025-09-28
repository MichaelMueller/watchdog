from typing import Literal, Optional, Any
from pydantic import BaseModel

from .bool_condition import BoolCondition

class In(BoolCondition):
    type:Literal["in"] = "in"
    values: list[Any]
    
    def evaluate(self, other: Any) -> bool:
        return other in self.values