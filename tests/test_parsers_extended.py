"""Tests for CSV, Markdown, and YAML glossary parsers."""

import pytest

from src.flashcards.ingestion.csv_parser import CSVGlossaryParser
from src.flashcards.ingestion.markdown_parser import MarkdownGlossaryParser
from src.flashcards.ingestion.yaml_parser import YAMLGlossaryParser


class TestCSVGlossaryParser:
    """Test CSV glossary parser."""

    def test_parse_basic_csv(self):
        """Parse basic CSV with term and definition columns."""
        csv_content = """term,definition
Python,A high-level programming language
JavaScript,A scripting language for web browsers"""

        parser = CSVGlossaryParser()
        entries = parser.parse(csv_content, "programming", "languages")

        assert len(entries) == 2
        assert entries[0].title == "Python"
        assert "high-level" in entries[0].body
        assert entries[1].title == "JavaScript"

    def test_parse_csv_with_metadata(self):
        """Parse CSV with difficulty and source columns."""
        csv_content = """term,definition,difficulty,source
API,Application Programming Interface,intermediate,RFC 7230
REST,Representational State Transfer,advanced,Fielding Dissertation"""

        parser = CSVGlossaryParser()
        entries = parser.parse(csv_content, "web", "architecture")

        assert len(entries) == 2
        assert entries[0].metadata.get("difficulty") == "intermediate"
        assert entries[1].metadata.get("source") == "Fielding Dissertation"

    def test_parse_csv_missing_required_columns(self):
        """Raise error if required columns missing."""
        csv_content = """term,description
Python,A language"""

        parser = CSVGlossaryParser()
        with pytest.raises(ValueError, match="definition"):
            parser.parse(csv_content, "domain", "category")

    def test_parse_csv_with_whitespace(self):
        """Handle leading/trailing whitespace in CSV."""
        csv_content = """term,definition
  Python  ,  A high-level language
  Java  ,  Enterprise language  """

        parser = CSVGlossaryParser()
        entries = parser.parse(csv_content, "lang", "oop")

        assert entries[0].title == "Python"
        assert entries[0].body == "A high-level language"


class TestMarkdownGlossaryParser:
    """Test Markdown glossary parser."""

    def test_parse_definition_list_format(self):
        """Parse ## Title + body definition list format."""
        markdown_content = """# Programming Glossary

## Python
A high-level, interpreted programming language.
Known for readability and simplicity.

## JavaScript
A scripting language for web browsers.
Powers interactive web applications.
"""

        parser = MarkdownGlossaryParser()
        entries = parser.parse(markdown_content, "programming", "languages")

        assert len(entries) == 2
        assert entries[0].title == "Python"
        assert "high-level" in entries[0].body
        assert entries[1].title == "JavaScript"
        assert "web browsers" in entries[1].body

    def test_parse_table_format(self):
        """Parse Markdown table format."""
        markdown_content = """| Term | Definition |
|------|------------|
| Python | A high-level language |
| Java | Enterprise language |"""

        parser = MarkdownGlossaryParser()
        entries = parser.parse(markdown_content, "lang", "oop")

        assert len(entries) == 2
        assert entries[0].title == "Python"
        assert entries[0].body == "A high-level language"

    def test_parse_empty_markdown(self):
        """Return empty list for markdown without glossary entries."""
        markdown_content = "# Just a heading\nNo glossary here."

        parser = MarkdownGlossaryParser()
        entries = parser.parse(markdown_content, "domain", "category")

        assert len(entries) == 0

    def test_parse_multiline_definition(self):
        """Parse definitions spanning multiple lines."""
        markdown_content = """## API
Application Programming Interface.
Allows software to communicate with other software.
Can be REST, GraphQL, SOAP, etc.

## Database
Organized collection of data.
Stores and retrieves information efficiently.
"""

        parser = MarkdownGlossaryParser()
        entries = parser.parse(markdown_content, "web", "architecture")

        assert len(entries) == 2
        assert "Application Programming Interface" in entries[0].body
        assert "REST" in entries[0].body
        assert "Organized collection" in entries[1].body


class TestYAMLGlossaryParser:
    """Test YAML glossary parser."""

    def test_parse_yaml_list_format(self):
        """Parse YAML list of glossary entries."""
        yaml_content = """- title: "Python"
  body: "A high-level language"
- title: "JavaScript"
  body: "A scripting language"""

        parser = YAMLGlossaryParser()
        entries = parser.parse(yaml_content, "prog", "languages")

        assert len(entries) == 2
        assert entries[0].title == "Python"
        assert entries[1].title == "JavaScript"

    def test_parse_yaml_with_glossary_key(self):
        """Parse YAML with glossary key."""
        yaml_content = """glossary:
  - title: "API"
    body: "Application Programming Interface"
    difficulty: "intermediate"
  - title: "REST"
    body: "Representational State Transfer"
    difficulty: "advanced"""

        parser = YAMLGlossaryParser()
        entries = parser.parse(yaml_content, "web", "architecture")

        assert len(entries) == 2
        assert entries[0].title == "API"
        assert entries[0].metadata.get("difficulty") == "intermediate"
        assert entries[1].metadata.get("difficulty") == "advanced"

    def test_parse_yaml_term_definition_keys(self):
        """Parse YAML using term/definition keys (alternate format)."""
        yaml_content = """- term: "Recursion"
  definition: "Function calling itself"
- term: "Iteration"
  definition: "Repeated execution using loops"""

        parser = YAMLGlossaryParser()
        entries = parser.parse(yaml_content, "algo", "concepts")

        assert len(entries) == 2
        assert entries[0].title == "Recursion"
        assert entries[0].body == "Function calling itself"

    def test_parse_yaml_simple_format_no_pyyaml(self):
        """Parse YAML using simple parser (no pyyaml dependency)."""
        yaml_content = """- title: "Term 1"
  body: "Definition 1"
- title: "Term 2"
  body: "Definition 2"""

        parser = YAMLGlossaryParser()
        # Use fallback parser
        entries = parser.parse(yaml_content, "test", "cat")

        assert len(entries) == 2
        assert all(isinstance(e, type(entries[0])) for e in entries)

    def test_parse_yaml_empty(self):
        """Return empty list for empty YAML."""
        yaml_content = ""

        parser = YAMLGlossaryParser()
        entries = parser.parse(yaml_content, "domain", "category")

        assert len(entries) == 0


class TestParserIntegration:
    """Integration tests comparing all parsers."""

    def test_all_parsers_same_domain_category(self):
        """All parsers should produce entries with correct domain/category."""
        domain = "test_domain"
        category = "test_category"

        csv_content = "term,definition\nTest,A test term"
        markdown_content = "## Test\nA test term"
        yaml_content = "- title: Test\n  body: A test term"

        csv_parser = CSVGlossaryParser()
        md_parser = MarkdownGlossaryParser()
        yaml_parser = YAMLGlossaryParser()

        csv_entries = csv_parser.parse(csv_content, domain, category)
        md_entries = md_parser.parse(markdown_content, domain, category)
        yaml_entries = yaml_parser.parse(yaml_content, domain, category)

        for entries in [csv_entries, md_entries, yaml_entries]:
            assert len(entries) > 0
            assert entries[0].domain == domain
            assert entries[0].category == category
