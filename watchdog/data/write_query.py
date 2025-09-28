from typing import Literal, Optional, List
from pydantic import BaseModel
from typing import TypeVar, Generic

from .query import Query

class WriteQuery(Query):
    type:str
    