import os
from dotenv import load_dotenv
from google import genai
import sys

def main():
# Load in the API Key
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Initialize google gen ai client
    client = genai.Client(api_key = api_key)

    if len(sys.argv) == 1 or len(sys.argv) > 3:
        print("Usage uv run main.py [PROMPT]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    messages = [
        prompt
    ]
    verbose = "--verbose" in sys.argv
    generate_content(client, messages, verbose)


def generate_content(client, messages, verbose):

    response = client.models.generate_content(
                model = "gemini-2.0-flash-001", 
                contents = messages)
    if "--verbose" in sys.argv:
        print(f"User prompt: {sys.argv[1]}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print(response.text)

if __name__ == "__main__":
    main()