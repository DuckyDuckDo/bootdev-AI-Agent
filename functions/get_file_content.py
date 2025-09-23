import os
from config import CHAR_LIMIT

def get_file_content(working_directory, file_path):
    full_path = os.path.join(working_directory, file_path)
    
    # Checks that file is within directory scope
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    # Checks that the path is a file
    if not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    # Reads up to CHAR_LIMIT characters from the file
    try:
        with open(full_path, "r") as f:
            file_content = f.read(CHAR_LIMIT)
            if os.path.getsize(full_path) > CHAR_LIMIT:
                content += (
                    f'[...File "{file_path}" truncated at {CHAR_LIMIT} characters]'
                )
        return file_content

    except Exception as e:
        return f'Error reading file "{file_path}": {e}'