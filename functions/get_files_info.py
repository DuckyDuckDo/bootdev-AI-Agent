import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)

    # Checks that we are staying within working directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')

    
    # Ensures directory parameter is an actual dir
    if not os.path.isdir(full_path):
        return(f'Error: "{directory}" is not a directory')

    # Tries to parse file information
    try:
        files_info = []
        for file in os.listdir(full_path):
            file_path = os.path.join(full_path, file)
            is_dir = os.path.isdir(file_path)
            file_size = os.path.getsize(file_path)
            files_info.append(f"- {file}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(files_info)
    
    except Exception as e:
        return f"Error listing files: {e}"