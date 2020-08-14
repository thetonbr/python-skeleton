from abc import abstractmethod, ABC
from typing import Dict, Any


class BaseController(ABC):
    @abstractmethod
    async def __call__(self, args: Dict[str, Any]) -> int:
        pass
