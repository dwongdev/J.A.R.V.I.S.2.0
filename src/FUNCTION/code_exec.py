import sys
import subprocess
import importlib
import os
from io import StringIO

def get_pip_command():
    """Returns the appropriate pip command based on the operating system."""
    if sys.platform == "win32":
        return "pip"  # Windows uses pip
    else:
        return "pip3"  # macOS/Linux uses pip3

def check_and_install_libraries(libraries):
    """
    Checks if required libraries are installed and installs any missing ones.
    Args:
        libraries (list): List of libraries to check and install if missing.
    """
    # File to store the installation status
    flag_file = './DATA/libraries_installed.txt'
    
    # Step 1: Check if the flag file exists
    if os.path.exists(flag_file):
        print("Libraries are already installed.")
        return  # Libraries are already installed, skip installation
    
    # If flag file does not exist, install missing libraries
    for library in libraries:
        try:
            importlib.import_module(library)
        except ImportError:
            print(f"Library '{library}' not found. Installing...")
            pip_command = get_pip_command()
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])
    
    # Step 2: Create the flag file to indicate libraries are installed
    with open(flag_file, 'w') as f:
        f.write("Libraries installed successfully.")


def execute_code_with_dependencies(code):
    """
    Executes the dynamically generated code and ensures that required libraries are installed.
    Args:
        code (str): The Python code to execute.
    
    Returns:
        dict: Dictionary containing the result or error message.
    """
    required_libraries = ['pandas', 'numpy', 'matplotlib']
    
    # Step 1: Install missing libraries if required
    check_and_install_libraries(required_libraries)

    # Initialize result dictionary
    result = {
        'output': None,
        'error': None,
    }

    # Step 2: Capture the output of the code execution
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Step 3: Execute the code in a clean context (no interference from the global scope)
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)

        # Step 4: Capture the output from print statements or results
        output = sys.stdout.getvalue()

        # Step 5: Return the result or output
        if not output:
            result['output'] = str(exec_locals)  # If no output, return the result of execution
        else:
            result['output'] = output
    
    except SyntaxError as e:
        result['error'] = f"Syntax Error: {e.msg} on line {e.lineno}"
    except NameError as e:
        result['error'] = f"Name Error: {e.args}"
    except Exception as e:
        result['error'] = f"Error during execution: {str(e)}"
    finally:
        sys.stdout = old_stdout  # Restore the original stdout

    return result

