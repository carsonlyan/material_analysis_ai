import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from src.logging_config import logger
from src import config


class MaterialPropertiesExtractor:
    """
    Extract material properties from XMT files.
    
    Args:
        data_dir: Directory containing XMT material files
        
    Example:
        >>> extractor = MaterialPropertiesExtractor(r"C:\materials\data")
        >>> properties = extractor.extract_all()
        >>> extractor.save_to_json("output.json")
    """
    
    def __init__(self, data_dir: str | Path) -> None:
        """
        Initialize the extractor with a data directory.
        
        Args:
            data_dir: Path to directory containing XMT files
        """
        self.data_dir = Path(data_dir)
        
        # Get properties from environment variable or config fallback
        target_properties_str = os.getenv('TARGET_PROPERTIES')
        if target_properties_str:
            logger.info(f"Using TARGET_PROPERTIES from environment: {target_properties_str} when initializing extractor")
            self.properties = [prop.strip() for prop in target_properties_str.split(',')]
        else:
            logger.info("Using default target properties from config when initializing extractor")
            self.properties = config.DEFAULT_PROPERTIES
        
        self.extracted_data = []
        
        if not self.data_dir.exists():
            logger.error(f"Directory not found: {data_dir}")
            raise FileNotFoundError(f"Directory not found: {data_dir}")
        
        logger.info(f"Initialized MaterialPropertiesExtractor for: {self.data_dir}")
    
    def extract_from_file(self, file_path: Path) -> dict:
        """
        Extract properties from a single XMT file.
        
        Args:
            file_path: Path to the XMT file
            
        Returns:
            dict: Dictionary with material properties
            
        Raises:
            Exception: If file parsing fails
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Get filename and group
        filename = os.path.basename(file_path)
        group = root.find('group')
        
        # Build result dictionary
        result = {
            "file_name": filename,
            "group": group.text if group is not None else None,
        }
        
        # Extract specified properties with units
        for prop in self.properties:
            element = root.find(prop)
            if element is not None and element.text:
                result[prop] = {
                    "value": float(element.text),
                    "unit": element.get('unit_symbol')
                }
            else:
                result[prop] = None
        
        return result
    
    def save_to_json(self, output_file: str = "material_properties.json", pretty: bool = True, print_incremental: bool = False) -> str:
        """
        Extract properties from all XMT files and save to JSON file.
        Optionally print each material as it's processed.
        
        Args:
            output_file: Output filename (default: "material_properties.json")
            pretty: Whether to format JSON with indentation (default: True)
            print_incremental: Whether to print each material as it's processed (default: False)
            
        Returns:
            str: Path to the saved file
            
        Example:
            >>> extractor = MaterialPropertiesExtractor(r"C:\data")
            >>> extractor.save_to_json()
            >>> extractor.save_to_json("output.json", print_incremental=True)
        """
        logger.info("Starting material properties extraction")
        
        # Find all .xmt files
        xmt_files = list(self.data_dir.glob("*.xmt"))
        logger.info(f"Found {len(xmt_files)} XMT files")
        
        self.extracted_data = []
        for idx, xmt_file in enumerate(xmt_files, 1):
            try:
                properties = self.extract_from_file(xmt_file)
                self.extracted_data.append(properties)
                
                # Print incrementally if requested
                if print_incremental:
                    indent = 2 if pretty else None
                    material_json = json.dumps(properties, indent=indent)
                    logger.info(f"[{idx}/{len(xmt_files)}] {properties['file_name']}:")
                    logger.info(material_json)
            except Exception as e:
                logger.error(f"Failed to extract properties from {xmt_file}: {e}")
                raise RuntimeError(f"Extraction failed for {xmt_file}. Aborting process.") from e
        
        logger.info(f"Successfully extracted properties from {len(self.extracted_data)} files")
        
        # Convert to JSON and save
        indent = 2 if pretty else None
        json_output = json.dumps(self.extracted_data, indent=indent)
        # Ensure the output directory exists to avoid write errors
        output_path = Path(output_file)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(json_output)
        logger.info(f"Results saved to {output_path}")
        
        return output_file

