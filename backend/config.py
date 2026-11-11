import os
from pathlib import Path

from dotenv import load_dotenv

required_groq_key_list = ["GROQ_KEY", "TOGETHER_API_KEY"]

def check_api_keys():

    load_dotenv(Path(__file__).parent/".env")
    missing = [ key for key in required_groq_key_list if not os.getenv(key)]
    if missing:
        raise ValueError(
            f"Error ( Clé(s) API absente(s) ou vide(s) dans le .env : {','.join(missing)})"
            )
    

if __name__ == "__main__":
    missing  = check_api_keys()
