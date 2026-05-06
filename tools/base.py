from abc import ABC, abstractmethod
from typing import Any

from tools.context import get_context


class BaseTool(ABC):
    """
    Abstract base class for all external tools.
    Implements the async context manager protocol for safe resource handling.
    """

    name: str
    description: str

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.teardown()

    async def setup(self):
        """Override to initialize resources (e.g., HTTP clients, DB connections)."""
        pass

    async def teardown(self):
        """Override to clean up resources."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """The core execution logic of the tool."""
        pass
