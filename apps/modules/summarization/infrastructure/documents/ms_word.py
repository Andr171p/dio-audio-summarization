from ...domain import Document
from .base import DocumentCompiler


class MsWordCompiler(DocumentCompiler):
    def compile(self, title: str, text: str) -> Document: ...
