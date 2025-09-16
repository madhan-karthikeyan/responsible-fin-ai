import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PDF_DIR = RAW_DATA_DIR / "pdfs"
DOWNLOADS_DIR = RAW_DATA_DIR / "downloads"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, PDF_DIR, DOWNLOADS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Optional, for OpenAI embeddings

# Vector DB Configuration
CHROMA_DB_PATH = str(BASE_DIR / "chroma_db")

# Scraping Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_DELAY = 2  # seconds between requests

# Investment data
INDIAN_TICKERS = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ITC.NS"]

# Tax year for data collection
CURRENT_TAX_YEAR = "2024-25"


print("Project structure and requirements file created!")
print("\nTo set up the project:")
print("1. Create a new directory: mkdir financial_planning_framework")
print("2. Save requirements.txt and config.py")
print("3. Install dependencies: pip install -r requirements.txt")
print("4. Optionally create .env file with OPENAI_API_KEY if using OpenAI embeddings")