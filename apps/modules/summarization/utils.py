from .domain import Document, DocumentFileMetadata, DocumentFormat
from .infrastructure.documents import DocumentCompiler, MsWordCompiler, PDFCompiler


def compile_document(title: str, text: str, format: DocumentFormat) -> Document:  # noqa: A002
    compiler = DocumentCompiler()
    match format:
        case DocumentFormat.DOCX:
            compiler = MsWordCompiler()
        case DocumentFormat.PDF:
            compiler = PDFCompiler()
    return compiler.compile(title, text)
