from typing import Literal, Optional, Type
from pydantic import BaseModel, Field
from typing import TypeVar, Generic

from .bool_condition import BoolCondition

class Descriptor(BoolCondition):
    
    def evaluate(self, obj:Type[BaseModel]) -> bool:
        if not isinstance(obj, BaseModel):
            return False

        for name in self.__class__.model_fields.keys():
            if name == "type":
                continue
            
            bool_condition:BoolCondition = getattr(self, name)
            if not isinstance(bool_condition, BoolCondition):
                raise ValueError(f"Field {name} is not a BoolCondition")
            
            if bool_condition is not None:
                target_value = getattr(obj, name, None)
                if not bool_condition.evaluate(target_value):
                    return False

        return True
    
    
