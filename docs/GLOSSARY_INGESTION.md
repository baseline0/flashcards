# Glossary Ingestion Pipeline

Complete guide for ingesting glossaries in multiple formats (JSON, CSV, Markdown, YAML).

## Overview

The ingestion pipeline transforms raw glossary files into `GlossaryEntry` objects that feed into the flashcards database and spaced repetition engine.

**Supported Formats:**
- JSON (structured data)
- CSV (tabular data)
- Markdown (document format)
- YAML (configuration format)

## Format Specifications

### JSON Format

**Structure:** Array of glossary entries with required fields.

```json
[
  {
    "title": "Python",
    "body": "A high-level, interpreted programming language known for readability.",
    "metadata": {
      "difficulty": "beginner",
      "source": "Wikipedia",
      "category": "programming_languages"
    }
  },
  {
    "title": "API",
    "body": "Application Programming Interface. Defines protocols for software communication.",
    "metadata": {
      "difficulty": "intermediate",
      "source": "RFC 7230"
    }
  }
]
```

**Parser:** `JSONGlossaryParser`

**Usage:**
```python
from src.flashcards.ingestion import JSONGlossaryParser

parser = JSONGlossaryParser()
entries = parser.parse(json_content, domain="programming", category="concepts")
```

### CSV Format

**Structure:** Comma-separated values with headers. Required columns: `term`, `definition`.

```csv
term,definition,difficulty,source
Python,A high-level programming language,beginner,Wikipedia
API,Application Programming Interface,intermediate,RFC 7230
Recursion,Function calling itself,advanced,CLRS
```

**Columns:**
- `term` (required): The glossary term/title
- `definition` (required): The term definition/body
- `difficulty` (optional): beginner/intermediate/advanced
- `source` (optional): Where the definition comes from
- `category` (optional): Override default category

**Parser:** `CSVGlossaryParser`

**Usage:**
```python
from src.flashcards.ingestion import CSVGlossaryParser

parser = CSVGlossaryParser()
entries = parser.parse(csv_content, domain="programming", category="languages")
```

### Markdown Format

**Format 1: Definition List**

Headings (##) for terms, followed by body text.

```markdown
# Programming Glossary

## Python
A high-level, interpreted programming language.
Known for readability and simplicity.
Great for beginners and experts alike.

## API
Application Programming Interface.
Allows software systems to communicate.
Supports REST, GraphQL, SOAP protocols.
```

**Format 2: Table**

Two-column table with Term and Definition.

```markdown
| Term | Definition |
|------|------------|
| Python | A high-level language |
| API | Application Programming Interface |
```

**Parser:** `MarkdownGlossaryParser`

**Usage:**
```python
from src.flashcards.ingestion import MarkdownGlossaryParser

parser = MarkdownGlossaryParser()
entries = parser.parse(markdown_content, domain="programming", category="concepts")
```

### YAML Format

**Structure:** YAML list with flexible key names (title/body or term/definition).

```yaml
glossary:
  - title: "Python"
    body: "A high-level programming language"
    difficulty: "beginner"
    source: "Wikipedia"
  - title: "API"
    body: "Application Programming Interface"
    difficulty: "intermediate"
    source: "RFC 7230"
```

**Alternative (shorter syntax):**
```yaml
- term: "Python"
  definition: "A high-level language"
- term: "API"
  definition: "Application Programming Interface"
```

**Parser:** `YAMLGlossaryParser`

**Features:**
- Supports both `title/body` and `term/definition` key pairs
- Works with or without `pyyaml` library (built-in fallback parser)
- Handles `glossary:`, `entries:`, or flat list formats

**Usage:**
```python
from src.flashcards.ingestion import YAMLGlossaryParser

parser = YAMLGlossaryParser()
entries = parser.parse(yaml_content, domain="programming", category="concepts")
```

## Parser Selection

Use the `get_parser()` helper to automatically select the right parser:

```python
from src.flashcards.ingestion import get_parser

# Automatically select parser based on format
parser = get_parser("json")      # JSONGlossaryParser
parser = get_parser("csv")       # CSVGlossaryParser
parser = get_parser("markdown")  # MarkdownGlossaryParser
parser = get_parser("yaml")      # YAMLGlossaryParser

# Parse content
entries = parser.parse(content, domain="web", category="architecture")
```

## Ingestion Workflow

### Step 1: Load Raw Content

```python
from pathlib import Path

glossary_file = Path("data/glossaries/aws_databases.json")
content = glossary_file.read_text()
```

### Step 2: Select Parser

```python
from src.flashcards.ingestion import get_parser

file_format = glossary_file.suffix.lstrip(".")  # "json"
parser = get_parser(file_format)
```

### Step 3: Parse Entries

```python
entries = parser.parse(
    content,
    domain="cloud_computing",
    category="AWS"
)

print(f"✓ Ingested {len(entries)} glossary entries")
```

### Step 4: Store in Database

```python
from src.flashcards.core.database import GlossaryDB

db = GlossaryDB()
for entry in entries:
    db.add_entry(entry)
db.commit()
```

## Metadata Handling

Each parser extracts and preserves metadata:

| Field | JSON | CSV | Markdown | YAML |
|-------|------|-----|----------|------|
| difficulty | ✓ | ✓ | metadata | ✓ |
| source | ✓ | ✓ | metadata | ✓ |
| category | ✓ | ✓ | metadata | ✓ |
| format | ✓ | ✓ | auto | ✓ |

Example metadata:
```python
entry.metadata = {
    "difficulty": "intermediate",
    "source": "RFC 7230",
    "category": "web_standards",
    "format": "json"
}
```

## Error Handling

### Missing Required Fields

```python
from src.flashcards.ingestion import CSVGlossaryParser

try:
    parser = CSVGlossaryParser()
    entries = parser.parse(csv_content, domain="test", category="test")
except ValueError as e:
    print(f"CSV error: {e}")
    # e.g., "CSV must have 'term' column"
```

### Format-Specific Issues

**JSON:**
- Must be valid JSON (use `json.JSONDecodeError`)
- Requires at least `title` and `body` keys

**CSV:**
- Must have `term` and `definition` columns
- Missing columns raise `ValueError`

**Markdown:**
- Recognizes `##` headings or `|...|` tables
- Returns empty list if no entries found (no error)

**YAML:**
- Falls back to simple parser if `pyyaml` not installed
- Handles missing keys gracefully

## Dashboard Metrics

Ingestion pipeline feeds these metrics to the fleet dashboard:

- **Glossary Coverage:** % of terms ingested vs. target
- **Format Distribution:** Breakdown by JSON/CSV/Markdown/YAML
- **Ingestion Rate:** Terms/minute during batch imports
- **Error Rate:** Failed entries vs. total attempts
- **Metadata Quality:** % of entries with difficulty, source, category

Example metrics export:

```json
{
  "domain": "cloud_computing",
  "total_terms": 42,
  "ingested": 38,
  "failed": 4,
  "formats_used": {
    "json": 15,
    "csv": 12,
    "markdown": 8,
    "yaml": 3
  },
  "metadata_coverage": {
    "difficulty": 0.89,
    "source": 0.76,
    "category": 1.0
  },
  "ingestion_speed_terms_per_min": 128
}
```

## Best Practices

1. **Choose the Right Format:**
   - **JSON:** For programmatic generation or APIs
   - **CSV:** For spreadsheet data (Excel, Google Sheets)
   - **Markdown:** For documentation and readability
   - **YAML:** For configuration or human-editable lists

2. **Validate Before Ingesting:**
   ```python
   # Check file format
   if not glossary_file.exists():
       raise FileNotFoundError(f"Glossary file not found: {glossary_file}")
   
   # Preview first entry
   parser = get_parser(file_format)
   entries = parser.parse(content, domain, category)
   print(f"First entry: {entries[0].title} → {entries[0].body[:50]}...")
   ```

3. **Batch Ingestion:**
   ```python
   from pathlib import Path
   
   glossary_dir = Path("data/glossaries")
   for glossary_file in glossary_dir.glob("*.json"):
       content = glossary_file.read_text()
       parser = get_parser(glossary_file.suffix.lstrip("."))
       entries = parser.parse(content, domain=glossary_file.stem, category="uncategorized")
       # Store entries...
   ```

4. **Metadata Enrichment:**
   - Always include `difficulty` for spaced repetition optimization
   - Add `source` for attribution and verification
   - Use `category` for organization and filtering

## Phase 5 Integration

The ingestion pipeline is part of Phase 5 (Dashboard & Orchestration):

- **Dashboard Metric:** Glossary ingestion % complete (target: 100%)
- **Health Report:** Ingestion errors per domain
- **Trend Tracking:** New terms added per week

See `docs/DASHBOARD_METRICS.md` for integration details.
