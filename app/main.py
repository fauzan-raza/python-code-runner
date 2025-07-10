# app/main.py
from flask import Flask, request, jsonify
from app.executor import execute_script_safely
import re

app = Flask(__name__)

def clean_nsjail_stderr(stderr):
    """Remove nsjail logging information from stderr"""
    if not stderr:
        return ""
    
    # Split into lines and filter out nsjail logs
    lines = stderr.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip nsjail info lines that start with [I][timestamp]
        if re.match(r'^\[I\]\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}\]', line):
            continue
        # Keep the line if it's not nsjail logging
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def create_clean_response(result, stdout):
    """Create a clean response without nsjail clutter"""
    
    # Clean the result if it contains stderr
    if isinstance(result, dict) and "stderr" in result:
        result = result.copy()  # Don't modify the original
        result["stderr"] = clean_nsjail_stderr(result["stderr"])
        
        # If stderr is now empty, remove it entirely
        if not result["stderr"]:
            del result["stderr"]
    
    # Check if the result indicates an error
    if isinstance(result, dict) and not result.get("success", True):
        # Return clean error response
        response = {
            "success": False,
            "error": result.get("error", "unknown_error"),
            "message": result.get("message", "An error occurred"),
            "stdout": stdout
        }
        
        # Add optional fields only if they exist and are meaningful
        if "error_type" in result:
            response["error_type"] = result["error_type"]
        if "suggestions" in result:
            response["suggestions"] = result["suggestions"]
        if "traceback" in result:
            response["traceback"] = result["traceback"]
        if "available_functions" in result:
            response["available_functions"] = result["available_functions"]
        if "return_code" in result:
            response["return_code"] = result["return_code"]
        
        return response
    else:
        # Success case
        return {
            "success": True,
            "result": result,
            "stdout": stdout
        }

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    script = data.get("script")
    
    if not script or not isinstance(script, str):
        return jsonify({
            "success": False,
            "error": "invalid_input",
            "message": "Invalid or missing 'script' parameter",
            "suggestions": ["Provide a valid Python script as a string"]
        }), 400
    
    try:
        result, stdout = execute_script_safely(script)
        response = create_clean_response(result, stdout)
        
        # Return appropriate HTTP status code
        status_code = 200 if response["success"] else 400
        return jsonify(response), status_code
            
    except Exception as e:
        # Handle any unexpected errors in the Flask app itself
        return jsonify({
            "success": False,
            "error": "internal_server_error",
            "message": str(e),
            "suggestions": ["Check server logs for more details", "Ensure the script execution service is running properly"]
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Python Script Executor",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)