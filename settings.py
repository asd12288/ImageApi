# settings.py

import os
from dotenv import load_dotenv, set_key
from pathlib import Path

# Load environment variables
load_dotenv()

def load_api_keys():
    BFL_API_KEY = os.getenv("BFL_API_KEY")
    IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
    return BFL_API_KEY, IDEOGRAM_API_KEY, STABILITY_API_KEY

def save_api_keys_to_env(bfl_key, ideogram_key, stability_key):
    env_path = Path('.') / '.env'
    set_key(str(env_path), 'BFL_API_KEY', bfl_key)
    set_key(str(env_path), 'IDEOGRAM_API_KEY', ideogram_key)
    set_key(str(env_path), 'STABILITY_API_KEY', stability_key)
