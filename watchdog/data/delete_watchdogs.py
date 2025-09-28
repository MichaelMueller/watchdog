from typing import List, Literal, Optional
from pydantic import Field

from .query import Query

class DeleteWatchdogs(Query):
    type:Literal["delete_watchdogs"] = "delete_watchdogs"
    names: List[str] = Field(..., min_length=1)