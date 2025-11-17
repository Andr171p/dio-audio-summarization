from abc import ABC, abstractmethod

from ...domain import Document


class DocumentCompiler(ABC):
    @abstractmethod
    def compile(self, title: str, text: str) -> Document: ...
