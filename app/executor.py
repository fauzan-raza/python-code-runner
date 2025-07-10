# app/executor.py
import os
import tempfile
import subprocess
import json
import uuid

NSJAIL_CONFIG = "/app/nsjail.cfg"  # path inside Docker container
WRAPPER_CODE = """
if __name__ == "__main__":
    import json
    result = main()
    with open("{result_path}", "w") as f:
        json.dump(result, f)
"""

def execute_script_safely(script: str):
    # Write script to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        result_path = tmp.name.replace(".py", ".result.json")
        full_script = script.strip() + "\n" + WRAPPER_CODE.format(result_path=result_path)
        tmp.write(full_script)
        script_path = tmp.name

    try:
        # Run script in nsjail using subprocess
        process = subprocess.run(
            [
                "nsjail",
                "--config", NSJAIL_CONFIG,
                "--",
                "python3", script_path
            ],
            capture_output=True,
            timeout=5,
            text=True
        )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode != 0:
            raise RuntimeError(f"Script execution failed: {stderr}")

        # Look for result file created by main()
        result_path = script_path.replace(".py", ".result.json")
        if not os.path.exists(result_path):
            raise RuntimeError("main() did not return a valid JSON result")

        with open(result_path) as f:
            result = json.load(f)

        return result, stdout

    finally:
        # Clean up
        os.remove(script_path)
        if os.path.exists(script_path.replace(".py", ".result.json")):
            os.remove(script_path.replace(".py", ".result.json"))
