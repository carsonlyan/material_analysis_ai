# Material Analysis AI

A Python tool for extracting and validating material properties from XMT files using Azure OpenAI.

## Features

- **Material Property Extraction**: Extracts yield strength, Young's modulus, and dissipation factor from XMT files
- **Batch Validation**: Validates extracted properties against standard material ranges using Azure OpenAI (gpt-5-mini)
- **Unit Preservation**: Extracts property values with their units from the `unit_symbol` attribute
- **Incremental Progress Logging**: Track extraction and validation progress in real-time
- **Rate Limit Handling**: Configurable intervals between API batches to avoid rate limits
- **Automatic Retry**: Built-in retry mechanism for API calls (max 3 retries)
- **Centralized Configuration**: All settings managed in `config.py`

## Project Structure

```
material_analysis_ai/
├── main.py                      # Entry point - orchestrates extraction and validation
├── src/                         # Source code
│   ├── __init__.py              # Package initialization
│   ├── material_extractor.py    # Extracts properties from XMT files
│   ├── batch_validator.py       # Validates properties using Azure OpenAI
│   ├── config.py                # Centralized configuration
│   └── logging_config.py        # Logging setup
├── output/                      # Generated JSON files (runtime output)
│   ├── material_properties.json # Extracted properties
│   └── validation_results.json  # Validation results
├── logs/                        # Log files (generated)
├── .env                         # Azure OpenAI API key (tracked for team sharing)
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

## Requirements

- Python 3.10+
- Azure OpenAI API access

### Dependencies

```bash
pip install openai python-dotenv
```

## Configuration

### Environment Variables

Create or update `.env` file:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
```

### Settings in `config.py`

- **AZURE_OPENAI_API_VERSION**: `"2024-12-01-preview"`
- **AZURE_OPENAI_ENDPOINT**: `"https://deqa-llm-1.openai.azure.com/"`
- **AZURE_OPENAI_MODEL**: `"gpt-5-mini"`
- **DEFAULT_BATCH_SIZE**: `50` materials per validation batch
- **DEFAULT_MATERIAL_DATA_DIR**: `r"C:\forming\simufact\material\data"`

## Usage

### Basic Usage

Run the complete extraction and validation pipeline:

```bash
python main.py
```

This will:
1. Extract properties from all XMT files in the configured directory
2. Save extracted data to `output/material_properties.json`
3. Validate properties in batches using Azure OpenAI
4. Save validation results to `output/validation_results.json`

### Advanced Usage

#### Extract Only

```python
from src.material_extractor import MaterialPropertiesExtractor

extractor = MaterialPropertiesExtractor(r"C:\path\to\materials")
extractor.save_to_json(output_file="output.json", print_incremental=True)
```

#### Validate Only

```python
from src.batch_validator import MaterialValidator

validator = MaterialValidator(batch_size=50)
result = validator.validate_all(
    materials_file="output/material_properties.json",
    batch_interval=5.0,  # Wait 5 seconds between batches
    max_batches=2        # Test with first 2 batches only
)
```

#### Custom Properties

```python
from src.material_extractor import MaterialPropertiesExtractor

extractor = MaterialPropertiesExtractor(
    data_dir=r"C:\materials",
    properties=["yield_strength", "tensile_strength", "hardness"]
)
```

## Output Format

### output/material_properties.json

```json
[
  {
    "file_name": "material1.xmt",
    "group": "Steel_304",
    "yield_strength": {
      "value": 215.0,
      "unit": "MPa"
    },
    "youngs_modulus": {
      "value": 200000.0,
      "unit": "MPa"
    },
    "dissipation_factor": {
      "value": 0.05,
      "unit": ""
    }
  }
]
```

### output/validation_results.json

```json
{
  "total_materials_checked": 100,
  "total_invalid": 2,
  "invalid_materials": [
    {
      "material_file": "material1.xmt",
      "material_name": "Steel_304",
      "invalid_properties": [
        {
          "property": "yield_strength",
          "value": 50.0,
          "unit": "MPa",
          "expected_range": "200-400 MPa"
        }
      ]
    }
  ]
}
```

## Features in Detail

### Property Extraction

- Extracts properties from XML nodes with both `value` and `unit_symbol` attributes
- Handles null/missing properties gracefully
- Provides incremental logging for long-running extractions
- Fail-fast approach: stops if any file fails to parse

### Validation

- **Batch Processing**: Validates 50 materials per API call by default
- **Null Handling**: Skips validation for null properties (doesn't report as invalid)
- **Rate Limiting**: Configurable delay between batches (default: 5 seconds)
- **Retry Logic**: Automatic retry up to 3 times on API failures
- **Smart Output**: Only reports materials with invalid properties

### Logging

- Dual output: Console (simple format) + File (detailed format with timestamps)
- Log file: `logs/material_analysis.log`
- Rotation: Creates new log directory if needed
- Centralized configuration via `logging_config.py`

## Error Handling

- **File Not Found**: Raises exception if data directory doesn't exist
- **XML Parsing Errors**: Stops execution if any XMT file is malformed
- **API Failures**: Retries up to 3 times, then raises exception
- **Rate Limits**: Configurable batch intervals to prevent hitting rate limits

## Development

### Type Safety

All functions use Python 3.10+ type hints:

```python
def validate_batch(self, materials_batch: list[dict], model: str | None = None) -> dict:
```

### Testing with Limited Batches

```python
# Test with first 2 batches (100 materials)
validator.validate_all(materials_file="output/material_properties.json", max_batches=2)
```

## Notes

- `.env` file is tracked in git for internal team API key sharing
- Output files in `output/` folder (`material_properties.json`, `validation_results.json`) are gitignored
- Log files are gitignored
- Uses modern Python syntax (Python 3.10+ required for `str | None` syntax)

## License

Internal use only.
