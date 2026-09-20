"""
Configuration settings for the material analysis project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_ENDPOINT = "https://deqa-llm-1.openai.azure.com/"
AZURE_OPENAI_MODEL = "gpt-5-mini"

# Material Extraction Configuration
DEFAULT_MATERIAL_DATA_DIR = r"C:\forming\simufact\material\data"
DEFAULT_OUTPUT_FILE = "output/material_properties.json"
DEFAULT_PROPERTIES = ["yield_strength", "youngs_modulus", "dissipation_factor"]

# Validation Configuration
DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_BATCHES = None  # None = process all batches, set to integer to limit
DEFAULT_VALIDATION_OUTPUT = "output/validation_results.json"

# Webhook Configuration
WEBHOOK_URL = "https://default1b16ab3eb8f64fe39f3e2db7fe549f.6a.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/b07868e09f8449cc80eb3dfc83ffe9d6/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=R0USg_L-mujY2nsCD-No6niJq4M-Ohg9TuUNrHS5jFA"

# API Key (loaded from environment variable)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
