"""Glossary ingestion pipelines."""

from .base import BaseGlossaryParser
from .csv_parser import CSVGlossaryParser
from .json_parser import JSONGlossaryParser
from .markdown_parser import MarkdownGlossaryParser
from .yaml_parser import YAMLGlossaryParser

__all__ = [
    "BaseGlossaryParser",
    "CSVGlossaryParser",
    "JSONGlossaryParser",
    "MarkdownGlossaryParser",
    "YAMLGlossaryParser",
    "get_parser",
]


def get_parser(format: str) -> BaseGlossaryParser:
    """Get parser for specified format.

    Args:
        format: One of 'json', 'csv', 'markdown', 'yaml'

    Returns:
        Instantiated parser for the format

    Raises:
        ValueError: If format is not supported
    """
    parsers = {
        "json": JSONGlossaryParser,
        "csv": CSVGlossaryParser,
        "markdown": MarkdownGlossaryParser,
        "md": MarkdownGlossaryParser,
        "yaml": YAMLGlossaryParser,
        "yml": YAMLGlossaryParser,
    }

    if format.lower() not in parsers:
        raise ValueError(
            f"Unsupported format: {format}. "
            f"Choose from: {', '.join(parsers.keys())}"
        )

    return parsers[format.lower()]()
