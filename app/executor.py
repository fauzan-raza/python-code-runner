import os
import tempfile
import subprocess
import json
import shutil
import traceback

NSJAIL_CONFIG = "/nsjail.cfg"

# Wrapper template constant
SCRIPT_WRAPPER_TEMPLATE = """import json
import sys
import os
import traceback
import inspect

# User script
{user_script}

# Execute main and capture result with graceful error handling
if __name__ == "__main__":
    result_data = {{"success": False}}
    
    try:
        # Check if main function exists
        if 'main' not in globals():
            available_functions = [name for name, obj in globals().items() 
                                 if callable(obj) and not name.startswith('_') and name != 'main']
            
            result_data = {{
                "success": False,
                "error": "missing_main",
                "message": "Script must contain a main() function as the entry point.",
                "available_functions": available_functions,
                "suggestions": [
                    "Add a main() function to your script",
                    "Example: def main():\\n    # Your code here\\n    return 'success'"
                ]
            }}
        else:
            # Check if main is actually callable
            if not callable(globals()['main']):
                result_data = {{
                    "success": False,
                    "error": "invalid_main",
                    "message": "'main' exists but is not a function."
                }}
            else:
                # Execute main function
                try:
                    # Get function signature info
                    sig = inspect.signature(main)
                    param_count = len(sig.parameters)
                    
                    print("Executing main() function...")
                    if param_count > 0:
                        print(f"Warning: main() function has {{param_count}} parameters, but none will be passed.")
                    
                    result = main()
                    
                    result_data = {{
                        "success": True,
                        "result": result,
                        "message": "Script completed successfully."
                    }}
                    
                    if result is not None:
                        print(f"Script completed successfully. Result: {{result}}")
                    else:
                        print("Script completed successfully.")
                        
                except Exception as e:
                    # Capture the full traceback
                    tb_str = traceback.format_exc()
                    
                    result_data = {{
                        "success": False,
                        "error": "runtime_error",
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "traceback": tb_str,
                        "suggestions": [
                            "Check your script logic for errors",
                            "Add try-except blocks for error handling",
                            "Use print statements for debugging"
                        ]
                    }}
                    
                    print(f"Script execution failed with error: {{type(e).__name__}}: {{e}}")
                    print(f"Full traceback:")
                    print(tb_str)
        
        # Write result to file
        with open("{result_path}", "w") as f:
            json.dump(result_data, f, indent=2)
            
        # Exit with appropriate code
        sys.exit(0 if result_data["success"] else 1)
        
    except Exception as e:
        # This catches any unexpected errors in the wrapper itself
        error_data = {{
            "success": False,
            "error": "wrapper_error",
            "message": f"Unexpected error in script wrapper: {{str(e)}}",
            "traceback": traceback.format_exc()
        }}
        
        with open("{result_path}", "w") as f:
            json.dump(error_data, f, indent=2)
        
        sys.exit(1)
"""

def execute_script_safely(script: str):
    """
    Execute a Python script safely in nsjail with graceful error handling
    
    Args:
        script: Python script content as string
        
    Returns:
        tuple: (result, stdout) where result is the execution result and stdout is captured output
    """
    # Create a temporary directory for this execution
    temp_dir = tempfile.mkdtemp(prefix="nsjail_exec_")
    
    try:
        # Write script to a temporary file in the temp directory
        script_path = os.path.join(temp_dir, "script.py")
        result_path = os.path.join(temp_dir, "result.json")
        
        # Generate the wrapper code using the template
        wrapper_code = SCRIPT_WRAPPER_TEMPLATE.format(
            user_script=script,
            result_path=result_path
        )
        
        with open(script_path, "w") as f:
            f.write(wrapper_code)
        
        # Run script in nsjail
        process = subprocess.run(
            [
                "nsjail",
                "--config", NSJAIL_CONFIG,
                "--",
                "/usr/local/bin/python3", script_path
            ],
            capture_output=True,
            timeout=10,
            text=True,
            cwd=temp_dir
        )
        
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        
        # Read result file if it exists
        result_data = None
        if os.path.exists(result_path):
            try:
                with open(result_path) as f:
                    result_data = json.load(f)
            except json.JSONDecodeError:
                result_data = {
                    "success": False,
                    "error": "json_decode_error",
                    "message": "Failed to parse result JSON"
                }
        
        # Handle different execution outcomes
        if process.returncode == 0:
            # Successful execution
            if result_data and result_data.get("success"):
                return result_data.get("result"), stdout
            elif result_data:
                # Script ran but had an error (e.g missing main or runtime error)
                return result_data, stdout
            else:
                # No result file but successful exit - shouldn't happen
                return {
                    "success": False,
                    "error": "no_result",
                    "message": "Script completed but produced no result"
                }, stdout
        else:
            # Failed execution
            if result_data:
                result_data["stdout"] = stdout
                result_data["stderr"] = stderr
                result_data["return_code"] = process.returncode
                return result_data, stdout
            else:
                raise RuntimeError(f"Script execution failed (return code {process.returncode}): {stderr}")
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "timeout",
            "message": "Script execution timed out (10 seconds limit)"
        }, ""
    except Exception as e:
        return {
            "success": False,
            "error": "system_error",
            "message": f"System error: {str(e)}"
        }, ""
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def is_error_result(result):
    """Check if the result from execute_script_safely indicates an error"""
    return isinstance(result, dict) and not result.get("success", True)


def handle_execute_request(script_content):
    """
    Handle an execute request with proper error responses
    
    Args:
        script_content: Python script content as string
        
    Returns:
        dict: Response data with 'response' and 'status_code' keys
    """
    try:
        result, stdout = execute_script_safely(script_content)
        
        if is_error_result(result):
            # Return error response with appropriate status code
            status_code = 400 if result["error"] in ["missing_main", "runtime_error", "invalid_main"] else 500
            return {
                "response": result,
                "status_code": status_code
            }
        else:
            # Success response
            return {
                "response": {
                    "success": True,
                    "result": result,
                    "stdout": stdout
                },
                "status_code": 200
            }
    except Exception as e:
        return {
            "response": {
                "success": False,
                "error": "handler_error",
                "message": f"Handler error: {str(e)}"
            },
            "status_code": 500
        }