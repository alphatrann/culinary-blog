from abc import ABC, abstractmethod


class Command:
    """Marker base for write requests. Subclass as a frozen dataclass; carries intent, changes state."""


class Query:
    """Marker base for read requests. Subclass as a frozen dataclass; must never change state."""


class CommandHandler[C: Command, R](ABC):
    @abstractmethod
    async def handle(self, command: C) -> R: ...


class QueryHandler[Q: Query, R](ABC):
    @abstractmethod
    async def handle(self, query: Q) -> R: ...
