from typing import Literal, Optional, Any
from pydantic import BaseModel

class BoolCondition(BaseModel):
    type:str
    
    def evaluate(self, obj:Any) -> bool:
        raise NotImplementedError()