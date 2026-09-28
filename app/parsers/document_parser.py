from pathlib import Path

from docling.document_converter import DocumentConverter


converter = DocumentConverter()


def parse_document(file_path: str) -> str:
    """
    Parse an invoice document and return its content as Markdown.
    """

    path = Path(file_path)

    result = converter.convert(path)

    document = result.document

    return document.export_to_markdown()