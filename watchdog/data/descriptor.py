from typing import Literal, Optional
from pydantic import BaseModel, Field
from typing import TypeVar, Generic

from .bool_condition import BoolCondition

T = TypeVar('T', bound='BaseModel')
class Descriptor(BoolCondition, Generic[T]):
    type:str
    target_cls: T = Field(default=None, exclude=True)
    
    def evaluate(self, obj: T) -> bool:
        if not isinstance(obj, BaseModel):
            return False

        for name in self.__class__.model_fields.keys():
            if name == "type":
                continue
            
            bool_condition:BoolCondition = getattr(self, name)
            
            if bool_condition is not None:
                target_value = getattr(obj, name, None)
                if not bool_condition.evaluate(target_value):
                    return False

        return True
    
    
