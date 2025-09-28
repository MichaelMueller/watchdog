from typing import Literal, Any, List, get_args, get_origin, Generic
from typing import get_type_hints
from .data.query import Query
from .data.insert import Insert
from .data.update import Update
from .data.delete import Delete
from .data.select import Select
from .data.write_query import WriteQuery
import asyncio, json
from pathlib import Path
import asyncio, json
from pathlib import Path
import inspect

class Db():
        
    def __init__(self, data_dir:str):
        self._data_dir = data_dir
        self._queued_queries:List[WriteQuery] = []

    def enqueue(self, query: WriteQuery) -> None:
        if not isinstance(query, WriteQuery):
            raise ValueError("Only WriteQuery instances can be enqueued")
        self._queued_queries.append(query)

    async def commit(self) -> List[Any]:
        results = []
        for query in self._queued_queries:
            result = await self.execute(query)
            results.append(result)
        self._queued_queries.clear()
        return results
    
    async def execute(self, select: Select) -> Any:
        target_class = select.__class__.model_fields["target_cls"].annotation
        print(f"Executing select query on {select.type} with target class {target_class}")