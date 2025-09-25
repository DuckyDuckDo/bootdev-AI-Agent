import os
import subprocess
import sys
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name = "run_python_file",
    description = "Runs a python file at specified file path along with any arguments",
    parameters = types.Schema(
        type = types.Type.OBJECT,
        properties = {
            "file_path": types.Schema(
                type = types.Type.STRING,
                description = "The path to the file to execute"
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the Python file.",
                ),
                description="Optional arguments to pass to the Python file.",
            ),
        },
        required=["file_path"],
    )
)
def run_python_file(working_directory, file_path, args = []):
    full_path = os.path.join(working_directory, file_path)

    # Checks for validity of file_path within working directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    # Checks file existence
    if not os.path.exists(full_path):
        return f'Error: File "{file_path}" not found.'
    
    # Checks that it is a python file
    if not full_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    # Set up script to run the file with passed in args
    try:
        passed_args = ["python", full_path]
        passed_args.extend(args) 
        result = subprocess.run(args = passed_args, timeout = 30, capture_output = True, text = True)

        output = []
        print(result)
        if result.stdout:
            output.append(f"STDOUT:\n {result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n {result.stderr}")

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        return "\n".join(output) if output else "No output produced."
        

    
    except Exception as e:
        return f"Error: executing Python file: {e}"