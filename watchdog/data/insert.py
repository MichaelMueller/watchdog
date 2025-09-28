from typing import Literal, Optional, List
from pydantic import BaseModel
from typing import TypeVar, Generic

from .write_query import WriteQuery

class Insert(WriteQuery):
    type:str
    
    def data(self) -> dict:
        return self.model_dump(exclude={"type"})