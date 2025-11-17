from ...domain import Document
from .base import DocumentCompiler


class PDFCompiler(DocumentCompiler):
    def compile(self, title: str, text: str) -> Document: ...
