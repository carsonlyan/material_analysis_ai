from src.batch_validator import MaterialValidator
from src.material_extractor import MaterialPropertiesExtractor
from src.logging_config import logger
from src.notification import send_webhook_notification
from src import config


def main():
    """Command-line entry point."""
    result = None
    error_occurred = False
    
    try:
        # Step 1: Extract material properties from XMT files
        extractor = MaterialPropertiesExtractor(config.DEFAULT_MATERIAL_DATA_DIR)
        extractor.save_to_json(
            output_file=config.DEFAULT_OUTPUT_FILE,
            print_incremental=True
        )
        
        # Step 2: Validate extracted properties
        validator = MaterialValidator(batch_size=config.DEFAULT_BATCH_SIZE)
        result = validator.validate_all(
            materials_file=config.DEFAULT_OUTPUT_FILE,
            batch_interval=30.0,
            max_batches=config.DEFAULT_MAX_BATCHES
        )
        
        logger.info("="*50)
        logger.info("Validation Summary:")
        logger.info(f"Total materials: {result['total_materials_checked']}")
        logger.info(f"Invalid materials: {result['total_invalid']}")
        logger.info("="*50)
    except Exception as e:
        error_occurred = True
        logger.error(f"Analysis failed: {e}")
        raise
    finally:
        # Step 3: Send webhook notification regardless of success/failure
        if hasattr(config, 'WEBHOOK_URL') and config.WEBHOOK_URL:
            if error_occurred:
                message = "Material Analysis Failed - An error occurred during processing"
            elif result:
                message = f"Material Analysis Complete - Total: {result['total_materials_checked']}, Invalid: {result['total_invalid']}"
            else:
                message = "Material Analysis Status Unknown"
            send_webhook_notification(message, config.WEBHOOK_URL)


if __name__ == "__main__":
    main()