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
    """
    response = client.models.generate_content(
                model = "gemini-2.0-flash-001", 
                contents = messages,
                config = GenerateContentConfig(tools = [available_functions], system_instruction = system_prompt))
    if "--verbose" in sys.argv:
        print(f"User prompt: {sys.argv[1]}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    # Calls the actual functions based on the prompt
    if response.function_calls:
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, verbose)
            if not function_call_result.parts[0].function_response.response:
                raise Exception('Fatal error with function calling')
            if verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

def call_function(function_call_part, verbose = False):
    """
    Helper function to call a function that the AI Agent decides to call based on prompt
    """
    # Dictionary of available functions to map name to function call
    function_dictionary = {
        'get_files_info': get_files_info,
        'get_file_content': get_file_content,
        'write_file': write_file,
        'run_python_file': run_python_file
    }

    # Controls console print messages of functions being called
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    if function_call_part.name not in function_dictionary:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )

    function_to_call = function_dictionary[function_call_part.name]
    
    # Call the function
    function_result = function_to_call(working_directory = './calculator', **function_call_part.args)

    # Return the result
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )



if __name__ == "__main__":
    main()