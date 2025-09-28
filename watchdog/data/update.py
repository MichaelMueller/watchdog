from typing import Literal, Optional, List
from pydantic import BaseModel
from typing import TypeVar, Generic

from .descriptor import Descriptor
from .write_query import WriteQuery

T = TypeVar('T', bound='BaseModel')
class Update(WriteQuery):
    type:str
    descriptor: Descriptor[T] = None
        
    def update(self, exisiting_data:dict) -> None:
        update_data = self.model_dump(exclude={"type", "descriptor"})
        exisiting_data.update(update_data)