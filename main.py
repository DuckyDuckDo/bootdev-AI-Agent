import os
from dotenv import load_dotenv
from google import genai
import sys

# Load in the API Key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize google gen ai client
client = genai.Client(api_key = api_key)

if len(sys.argv) != 2:
    print("Usage uv run main.py [PROMPT]")
    sys.exit(1)



response = client.models.generate_content(
            model = "gemini-2.0-flash-001", 
            contents = sys.argv[1])

print(response.text)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Response tokens: {response.usage_metadata.candidates_token_count}")