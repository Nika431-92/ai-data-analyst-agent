
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("SUCCESS: Gemini API key found!")
else:
    print("ERROR: GEMINI_API_KEY not found.")
    print("Check that your .env file is in the project root.")

