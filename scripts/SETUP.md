# 🎮 Kaetram API Test Suite Setup Guide

## 📋 Prerequisites

Before starting, ensure your system has the following software installed:

### Required Components
- **Node.js** (version >= 16.0.0)
- **Python** (version >= 3.8.0)
- **Git** (for project cloning)

### Optional Components
- **MongoDB** (for testing complete database functionality)
- **Docker** (for containerized deployment)

## 🚀 Quick Start

### 1. Environment Check
```bash
# Check Node.js version
node --version

# Check Python version
python3 --version

# Check npm version
npm --version

# Check pip version
pip3 --version
```

### 2. Configure Test Parameters
Edit the `config.json` file and adjust the following parameters according to your environment:

```json
{
  "server": {
    "host": "localhost",
    "port": 9001,
    "base_url": "http://localhost:9001"
  },
  "hub": {
    "host": "localhost", 
    "port": 9002,
    "base_url": "http://localhost:9002",
    "access_token": "your-hub-access-token"
  },
  "test_settings": {
    "timeout": 30,
    "retry_count": 3,
    "parallel_tests": true,
    "cleanup_after_tests": true
  },
  "logging": {
    "level": "INFO",
    "console": true,
    "file": "test_reports/test.log"
  }
}
```

### 3. Install Dependencies

#### Python Environment
```bash
# Navigate to scripts directory
cd scripts

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import requests, colorlog, tabulate; print('Python dependencies installed successfully')"
```

#### JavaScript/Node.js Environment
```bash
# Navigate to scripts directory
cd scripts

# Install Node.js dependencies
npm install

# Verify installation
node -e "console.log('Node.js dependencies installed successfully')"
```

### 4. Run Tests

#### Python Tests
```bash
# Run all tests
python python/run_all_tests.py

# Run specific test suite
python python/test_server_api.py
python python/test_hub_api.py
python python/test_ai_agent.py

# Run tests with options
python python/run_all_tests.py --verbose --parallel --cleanup
```

#### JavaScript Tests
```bash
# Run all tests
node javascript/run_all_tests.js

# Run specific test suite
node javascript/test_server_api.js
```

## 📊 Test Results

All test results are automatically saved to the `test_reports/` directory:

- **test_results.json** - Raw test result data
- **test_results.html** - HTML formatted test report
- **test.log** - Detailed execution logs
- **error.log** - Error logs (if any errors occur)

## 🔧 Advanced Configuration

### Environment Variables
You can override configuration values using environment variables:

```bash
export KAETRAM_SERVER_HOST=localhost
export KAETRAM_SERVER_PORT=9001
export KAETRAM_HUB_HOST=localhost
export KAETRAM_HUB_PORT=9002
```

### Custom Test Data
Create custom test data files in the `test_data/` directory:

```json
{
  "test_agents": [
    {
      "username": "test_agent_1",
      "password": "testpass123"
    }
  ],
  "test_scenarios": [
    {
      "name": "basic_movement",
      "steps": ["create_agent", "login", "move", "logout"]
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Connection Refused
```
Error: connect ECONNREFUSED 127.0.0.1:9001
```
**Solution**: Ensure the game server is running on the correct port.

#### 2. Module Not Found
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Install Python dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Permission Denied
```
Error: EACCES: permission denied
```
**Solution**: Run with appropriate permissions or use virtual environment.

#### 4. Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::9001
```
**Solution**: Check if another process is using the port:
```bash
# On Linux/Mac
lsof -i :9001

# On Windows
netstat -ano | findstr :9001
```

### Debug Mode
Enable debug mode for detailed logging:

```bash
# Python
python python/run_all_tests.py --debug

# Set log level in config.json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Performance Optimization
For faster test execution:

```json
{
  "test_settings": {
    "parallel_tests": true,
    "timeout": 15,
    "retry_count": 2
  }
}
```

## 🔒 Security Notes

- Never commit real credentials to version control
- Use environment variables for sensitive data
- Regularly rotate test account passwords
- Limit test account permissions

## 📚 Additional Resources

### API Documentation
- [Kaetram Server API](../docs/server_api.md)
- [Kaetram Hub API](../docs/hub_api.md)
- [WebSocket API](../docs/websocket_api.md)

### Development Tools
- [Postman Collection](../tools/postman_collection.json)
- [Insomnia Workspace](../tools/insomnia_workspace.json)

## 🤝 Contributing

To add new tests:

1. Follow the existing test pattern
2. Use the provided utility functions
3. Add proper error handling
4. Include test documentation
5. Update this setup guide if needed

### Test Structure
```python
def test_feature_name(self) -> Dict[str, Any]:
    """Test description"""
    # Test implementation
    response = self.suite.client.get("/api/endpoint")
    data = validate_response(response)
    
    # Assertions
    if 'expected_field' not in data:
        raise ValueError("Missing expected field")
    
    return data
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs in `test_reports/`
3. Verify your configuration
4. Check server status
5. Create an issue with detailed error information

---

**Happy Testing! 🎉** 