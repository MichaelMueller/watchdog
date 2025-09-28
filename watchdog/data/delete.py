from typing import Literal, Optional, List
from pydantic import BaseModel
from typing import TypeVar, Generic

from .descriptor import Descriptor
from .write_query import WriteQuery

T = TypeVar('T', bound='BaseModel')
class Delete(WriteQuery):
    type:str
    descriptor: Descriptor[T] = None