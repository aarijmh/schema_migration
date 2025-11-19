# Schema Migrator

Convert Playwright test scripts to structured JSON schema format for automated test execution.

## Features

- **Playwright to Schema**: Converts Playwright Python scripts to JSON schema
- **Helper Function Support**: Handles `fill_text_fields()`, `select_dropdowns()`, `upload_files()` functions
- **AI-Powered Mapping**: Uses OLLAMA for intelligent action mapping
- **Fallback Parsing**: Manual regex parsing when AI fails
- **Multiple Action Types**: Supports fill, click, select, upload, hover, visit actions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Migration

```python
from playwright_to_schema_migrator import PlaywrightToSchemaMigrator

migrator = PlaywrightToSchemaMigrator()
migrator.migrate_script("test_script.py", "output_schema.json")
```

### Command Line

```bash
python playwright_to_schema_migrator.py
```

## Supported Actions

| Playwright Action | Schema Command | Description |
|------------------|----------------|-------------|
| `page.goto()` | `visit` | Navigate to URL |
| `page.fill()` | `type` | Fill text input |
| `page.click()` | `click` | Click element |
| `page.select_option()` | `select` | Select dropdown |
| `page.set_input_files()` | `upload` | Upload file |
| `page.hover()` | `hover` | Hover element |

## Input Format

Playwright script with helper functions:

```python
def fill_text_fields(page, fields):
    for selector, value in fields.items():
        page.fill(selector, value)

text_fields_step1 = {
    "#firstName": "John",
    "#email": "john@example.com"
}
fill_text_fields(page, text_fields_step1)
```

## Output Format

```json
[{
  "steps": [{
    "command": {
      "name": "type",
      "fields": [{
        "name": "name",
        "type": "text",
        "label": "Name",
        "value": "John",
        "required": true
      }]
    },
    "order": 1
  }],
  "name": "migratedTest",
  "base_url": "https://example.com"
}]
```

## Configuration

Set OLLAMA URL in the migrator:

```python
migrator = PlaywrightToSchemaMigrator(ollama_url="http://localhost:11434")
```

## File Structure

```
schema_migrator/
├── playwright_to_schema_migrator.py  # Main migrator
├── sample_scripts/
│   ├── test_1.py                     # Simple test
│   └── test_2.py                     # Complex test
├── sample_schemas/
│   └── CustomerCreate.json           # Schema reference
└── requirements.txt                  # Dependencies
```

## Requirements

- Python 3.7+
- requests
- OLLAMA (optional, for AI mapping)

## License

MIT