from typing import Literal, Optional, Any
from pydantic import BaseModel

from .bool_condition import BoolCondition

class Or(BoolCondition):
    type:Literal["or"] = "or"
    conditions: list[BoolCondition]
    
    def evaluate(self, other: Any) -> bool:
        return any(condition.evaluate(other) for condition in self.conditions)