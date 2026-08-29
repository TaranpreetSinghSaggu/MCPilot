from abc import ABC, abstractmethod
from typing import Any


class BaseIntegration(ABC):

    platform: str

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get(self, path: str, **kwargs: Any) -> Any:
        raise NotImplementedError