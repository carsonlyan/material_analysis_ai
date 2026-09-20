import json
import os
import time
from pathlib import Path
from openai import AzureOpenAI
from src.logging_config import logger
from src import config


class MaterialValidator:
    """Validate material properties in batches using Azure OpenAI."""
    
    def __init__(self, batch_size: int = 50) -> None:
        """
        Initialize validator.
        
        Args:
            batch_size: Number of materials to validate per API call (default: 50)
        """
        self.batch_size = batch_size
        self.client = AzureOpenAI(
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            max_retries=3,
        )
    
    def validate_batch(self, materials_batch: list[dict], model: str | None = None) -> dict:
        """
        Validate a batch of materials.
        
        Args:
            materials_batch: List of material dictionaries
            model: Model to use (default: gpt-4o-mini)
            
        Returns:
            dict: Validation results for the batch
        """
        model = model or config.AZURE_OPENAI_MODEL
        materials_json = json.dumps(materials_batch, indent=2)
        
        # Get target properties from environment variable or fallback to config
        target_properties_str = os.getenv('TARGET_PROPERTIES')
        if target_properties_str:
            logger.info(f"Using TARGET_PROPERTIES from environment: {target_properties_str}")
            target_properties = [prop.strip() for prop in target_properties_str.split(',')]
        else:
            logger.info("Using default target properties from config")
            target_properties = config.DEFAULT_PROPERTIES
        
        properties_list = ', '.join([f'"{prop}"' for prop in target_properties])
        
        prompt = f"""
Analyze these materials and validate their properties against standard ranges:

{materials_json}

Instructions:
1. Identify each material from the "group" field
2. Check these properties: {properties_list}
3. IMPORTANT: If a property is null, skip it - do NOT validate or report it as invalid
4. Only validate properties that have actual numeric values
5. Each property has "value" and "unit" fields - include BOTH in your response
6. Validate if each non-null property falls within proper ranges for that material type
7. Return ONLY materials with invalid properties
8. Whitelist: If `dissipation_factor` equals 0.9, treat it as valid and do not report it as invalid (this value is allowed)

Return format:
{{
    "invalid_materials": [
        {{
            "material_file": "filename.xmt",
            "material_name": "material_group",
            "invalid_properties": [
                {{
                    "property": "property_name",
                    "value": actual_value,
                    "unit": "unit_from_input",
                    "expected_range": "min-max"
                }}
            ]
        }}
    ]
}}

If all properties are valid, return: {{"invalid_materials": []}}
"""
        
        logger.info(f"Validating batch of {len(materials_batch)} materials")
        
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a materials engineering expert. Validate properties against industry standards."},
                {"role": "user", "content": prompt}
            ]
        )
        
        response_content = completion.choices[0].message.content
        return json.loads(response_content)
    
    def validate_all(self, materials_file: str, output_file: str | None = None, model: str | None = None, max_batches: int | None = None, batch_interval: float = 5.0) -> dict:
        """
        Validate all materials from a JSON file in batches.
        
        Args:
            materials_file: Path to material_properties.json
            output_file: Output file for validation results
            model: Model to use
            max_batches: Maximum number of batches to process (None for all)
            batch_interval: Seconds to wait between batches to avoid rate limits (default: 5.0)
            
        Returns:
            dict: Combined validation results
        """
        output_file = output_file or config.DEFAULT_VALIDATION_OUTPUT
        model = model or config.AZURE_OPENAI_MODEL
        
        logger.info(f"Loading materials from {materials_file}")
        
        with open(materials_file, 'r') as f:
            all_materials = json.load(f)
        
        total = len(all_materials)
        total_batches = (total + self.batch_size - 1) // self.batch_size
        
        # Limit batches if max_batches is specified
        if max_batches:
            total_batches = min(total_batches, max_batches)
            logger.info(f"Limiting to first {max_batches} batches")
        
        # Calculate actual number of materials to check
        materials_to_check = min(total, total_batches * self.batch_size)
        
        logger.info(f"Validating {materials_to_check} materials in batches of {self.batch_size}")
        
        all_invalid = []
        
        # Process in batches
        for i in range(0, materials_to_check, self.batch_size):
            batch = all_materials[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            result = self.validate_batch(batch, model)
            invalid = result.get('invalid_materials', [])
            all_invalid.extend(invalid)
            logger.info(f"Batch {batch_num}: Found {len(invalid)} invalid materials")
            
            # Wait between batches to avoid rate limits (except for last batch)
            if batch_num < total_batches:
                logger.info(f"Waiting {batch_interval} seconds before next batch...")
                time.sleep(batch_interval)
        
        # Combine results
        final_result = {
            "total_materials_checked": materials_to_check,
            "total_invalid": len(all_invalid),
            "invalid_materials": all_invalid
        }

        output_path = Path(output_file)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(final_result, f, indent=2)
        
        logger.info(f"Validation complete: {len(all_invalid)} invalid materials found")
        logger.info(f"Results saved to {output_file}")
        
        return final_result

