import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def get_api_key(api_name):
    key = os.getenv(f"{api_name.upper()}_API_KEY")
    if not key:
        raise ValueError(f"API key for {api_name} not found in environment variables")
    return key
