# app/main.py
from flask import Flask, request, jsonify
from app.executor import execute_script_safely

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    script = data.get("script")

    if not script or not isinstance(script, str):
        return jsonify({"error": "Invalid or missing 'script'"}), 400

    try:
        result, stdout = execute_script_safely(script)
        return jsonify({"result": result, "stdout": stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
