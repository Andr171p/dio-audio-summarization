from abc import ABC, abstractmethod

from ..domain import EmailLetter


class EmailSender(ABC):
    """Отправляет email письма"""

    @abstractmethod
    async def send(self, letter: EmailLetter) -> None: ...
