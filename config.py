from pathlib import Path

# Project configuration
PROJECT_DIR = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = PROJECT_DIR / "processed"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# OpenAI configuration
OPENAI_MODEL = "gpt-4-1106-preview"  # You can change this to your preferred model 