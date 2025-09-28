from typing import Literal
from pydantic import BaseModel

class Query(BaseModel):
    type:str
