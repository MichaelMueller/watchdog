from typing import Literal, Optional, List,Type, ClassVar
from pydantic import BaseModel, Field
from typing import TypeVar, Generic

from .bool_condition import BoolCondition
from .query import Query
from .descriptor import Descriptor

T = TypeVar('T', bound='BaseModel')
class Select(Query, Generic[T]):    
    
    target_cls: T = Field(default=None, exclude=True)
    
    descriptors: List[ Descriptor ] = []
    limit: Optional[int] = None
    offset: Optional[int] = None

    def evaluate(self, obj: T) -> bool:
        equals = False
        for descriptor in self.descriptors or []:
            equals = equals or descriptor.evaluate(obj)
        return equals
