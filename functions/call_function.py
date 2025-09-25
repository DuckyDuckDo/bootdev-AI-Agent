from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file

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
