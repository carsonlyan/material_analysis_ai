"""
Centralized logging configuration for the material analysis project.
Import get_logger() in any module to use consistent logging across the project.
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_dir="logs"):
    """
    Configure logging once for the entire application.
    
    Args:
        log_level: The logging level (default: logging.INFO)
        log_dir: Directory to store log files (default: "logs")
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # File handler for all logs (detailed format)
    file_handler = logging.FileHandler(log_path / 'material_analysis.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # File handler for errors only
    error_handler = logging.FileHandler(log_path / 'errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Prevent propagation issues
    root_logger.propagate = False
    
    # Log initial setup
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log directory: {log_path.absolute()}")


# Initialize logging when this module is imported
# This ensures logging is configured before any other module uses it
if not logging.getLogger().handlers:
    setup_logging()

# Export a pre-configured logger for direct import
logger = logging.getLogger('material_analysis')
