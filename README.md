# Python Script Executor API

A secure, containerized Python script execution service built with Flask and nsjail for safe code execution in isolated environments.

## Features

- 🔒 **Secure Execution**: Uses nsjail for sandboxed script execution
- 🐳 **Containerized**: Fully containerized with Docker for easy deployment
- 🚀 **RESTful API**: Simple HTTP API for script execution
- 📊 **Detailed Error Reporting**: Comprehensive error messages with suggestions
- 🛡️ **Resource Limits**: Built-in timeouts and resource constraints
- 🔍 **Function Analysis**: Detects available functions in scripts
- 📝 **Clean Output**: Filtered responses without system noise

## Quick Start

### Using Docker (Recommended)

```bash
# Build the container
docker build -t python-code-runner .

# Run the service
docker run -p 8080:8080 python-code-runner
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m app.main
```

## API Reference

### Execute Script

**Endpoint:** `POST /execute`

**Request:**
```json
{
  "script": "def main():\n    return 'Hello, World!'"
}
```

**Success Response:**
```json
{
  "success": true,
  "result": "Hello, World!",
  "stdout": "Executing main() function...\nHello, World!"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "missing_main",
  "message": "Script must contain a main() function as the entry point.",
  "stdout": "",
  "suggestions": [
    "Add a main() function to your script",
    "Example: def main():\n    # Your code here\n    return 'success'"
  ],
  "available_functions": ["other_function"],
  "return_code": 1
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Python Script Executor",
  "version": "1.0.0"
}
```

## Script Requirements

All scripts must contain a `main()` function as the entry point:

```python
def main():
    # Your code here
    return "success"
```

## Error Types

| Error Type | Description | Common Causes |
|------------|-------------|---------------|
| `missing_main` | Script lacks a main() function | Forgot to define main() |
| `syntax_error` | Python syntax error | Invalid Python syntax |
| `runtime_error` | Runtime exception occurred | Logic errors, undefined variables |
| `timeout` | Script execution timed out | Infinite loops, long-running code |
| `invalid_input` | Invalid request format | Missing script parameter |

## Examples

### Basic Script
```bash
curl -X POST http://127.0.0.1:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return \"Hello, World!\""}'
```

### Script with Print Statements
```bash
curl -X POST http://127.0.0.1:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Processing...\")\n    return sum([1, 2, 3, 4, 5])"}'
```

### Script with Error Handling
```bash
curl -X POST http://127.0.0.1:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    try:\n        return 10 / 0\n    except ZeroDivisionError:\n        return \"Cannot divide by zero!\""}'
```

## Security Features

- **Sandboxed Execution**: Scripts run in isolated nsjail containers
- **Resource Limits**: 10-second execution timeout
- **Read-only File System**: Scripts cannot modify the host system
- **No Network Access**: Scripts cannot make external network calls
- **Memory Limits**: Prevents memory exhaustion attacks

## Configuration

### nsjail Configuration

The service uses nsjail with the following security settings:
- Read-only root filesystem
- No network access
- Process isolation
- Resource limits
- Temporary directory restrictions

## Development

### Project Structure
```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # Flask application
│   └── executor.py         # Script execution logic
├── nsjail.cfg              # nsjail configuration
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Test the service
curl -X GET http://127.0.0.1:8080/health

# Test script execution
curl -X POST http://127.0.0.1:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return \"test\""}'
```

### Adding New Features

1. **Extend the executor**: Modify `app/executor.py` for execution logic
2. **Add API endpoints**: Update `app/main.py` for new routes
3. **Update security**: Modify `nsjail.cfg` for sandbox settings

## Troubleshooting

### Common Issues

**Container fails to start:**
```bash
# Check logs
docker logs <container-id>

# Verify nsjail installation
docker run -it python-code-runner nsjail --help
```

**Scripts timing out:**
- Check for infinite loops
- Reduce computational complexity
- Consider increasing timeout (not recommended for production)

**Permission errors:**
- Ensure Docker has proper permissions
- Check nsjail configuration

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_DEBUG=True
python -m app.main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Note**: This service is designed for educational and development purposes. For production use, consider additional security measures and monitoring.