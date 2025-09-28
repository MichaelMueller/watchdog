from typing import TypeVar, Generic

T = TypeVar('T')
class Functor(Generic[T]):
    
    async def run(self) -> T:
        raise NotImplementedError()
    
    async def __call__(self, *args, **kwargs) -> T:
        return await self.run(*args, **kwargs)