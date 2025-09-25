import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai.types import GenerateContentConfig
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.call_function import call_function

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

    for i in range(20):
        print(f"{i+1} ------------ \n")
        try:
            response = generate_content(client, messages, verbose)
            if response:
                print(f'"Final Response": {response}')
                return 
            
        except Exception as e:
            print(e)
            return 




######### HELPER FUNCTIONS ################
def generate_content(client, messages, verbose):
    available_functions = types.Tool(
        function_declarations=[
            schema_run_python_file,
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file
        ]
    )
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons. 
    After coming up with a plan, feel free to call said functions and execute the plan. 
    """
    response = client.models.generate_content(
                model = "gemini-2.0-flash-001", 
                contents = messages,
                config = GenerateContentConfig(tools = [available_functions], system_instruction = system_prompt))
    if "--verbose" in sys.argv:
        print(f"User prompt: {sys.argv[1]}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    # If there is a response, add the model response to the messages
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    # If no function calls are present, this is the end of the agent workflow, returns the final text response
    if not response.function_calls:
        return response.text
    
    # If there are function calls, decide them, and execute them here
    if response.function_calls:
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, verbose)
            if not function_call_result.parts[0].function_response.response:
                raise Exception('Fatal error with function calling')
            if verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
            
            # Add any results of function calls to the AI conversation
            message_to_add = types.Content(
                role = "user",
                parts = [types.Part.from_text(
                    text = f"This is the result from {function_call_result.parts[0].function_response.name}: {function_call_result.parts[0].function_response.response}"
                )]
            )
            messages.append(message_to_add)

if __name__ == "__main__":
    main()