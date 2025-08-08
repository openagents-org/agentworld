# API Testing Scripts Collection

This folder contains testing scripts for all Kaetram game API endpoints.

## 📁 File Structure

```
scripts/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
├── config.json                  # Configuration file
├── python/                      # Python test scripts
│   ├── test_server_api.py       # Game server API tests
│   ├── test_hub_api.py          # Hub API tests
│   ├── test_ai_agent.py         # AI agent complete workflow tests
│   └── run_all_tests.py         # Run all Python tests
├── javascript/                  # JavaScript test scripts
│   ├── test_server_api.js       # Game server API tests
│   ├── test_hub_api.js          # Hub API tests
│   ├── test_ai_agent.js         # AI agent complete workflow tests
│   └── run_all_tests.js         # Run all JS tests
└── utils/                       # Utility functions
    ├── test_utils.py            # Python utility functions
    └── test_utils.js            # JavaScript utility functions
```

## 🚀 Quick Start

### Python Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python python/run_all_tests.py

# Run individual test
python python/test_server_api.py
```

### JavaScript Environment
```bash
# Install dependencies
npm install

# Run all tests
node javascript/run_all_tests.js

# Run individual test
node javascript/test_server_api.js
```

## 🔧 Configuration

Edit `config.json` to configure test parameters:

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
    "base_url": "http://localhost:9002"
  },
  "test_settings": {
    "timeout": 30,
    "retry_count": 3
  }
}
```

## 🎯 Test Categories

### 1. Server API Tests
- Server information query
- AI agent creation and management
- Character movement and combat
- Resource collection and crafting
- Equipment and inventory management

### 2. Hub API Tests
- Server status and management
- Player online status queries
- Leaderboard data retrieval
- Account management features

### 3. AI Agent Workflow Tests
- Complete game flow simulation
- Real player behavior mimicking
- Multi-scenario testing
- Performance and stability testing

## 📊 Test Results

Test results are automatically saved to the `test_reports/` directory:
- `test_results.json` - Complete test result data
- `test_results.html` - HTML format test report
- `test.log` - Detailed test execution logs

## 🧪 Custom Tests

You can create custom tests by extending the base test classes:

```python
from utils.test_utils import TestSuite, TestConfig

class CustomTests:
    def __init__(self, config: TestConfig):
        self.suite = TestSuite("CustomTests", config)
        
    def test_custom_feature(self):
        # Your test implementation
        pass
```

## 📝 Notes

- Ensure the game server and hub are running before executing tests
- Some tests may require special permissions or configurations
- Check the logs for detailed error information if tests fail
- Clean up test data regularly to avoid conflicts 