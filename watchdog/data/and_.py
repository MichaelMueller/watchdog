from typing import Literal, Optional, Any
from pydantic import BaseModel

from .bool_condition import BoolCondition

class And(BoolCondition):
    type:Literal["and"] = "and"
    conditions: list[BoolCondition]
    
    def evaluate(self, other: Any) -> bool:
        return all(condition.evaluate(other) for condition in self.conditions)