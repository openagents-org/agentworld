"""
Kaetram API Test Utility Functions
"""
import json
import time
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import requests
import colorlog
from tabulate import tabulate

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestConfig:
    """Test configuration class"""
    def __init__(self, config_file: str = "config.json"):
        self.config_path = Path(__file__).parent.parent / config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Configuration file format error: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

class Logger:
    """Logger class"""
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = self.setup_logger()
    
    def setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger('kaetram_test')
        logger.setLevel(getattr(logging, self.config.get('logging.level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        if self.config.get('logging.console', True):
            console_handler = colorlog.StreamHandler()
            console_handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(console_handler)
        
        # File handler
        log_file = self.config.get('logging.file', 'test_reports/test.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class APIClient:
    """API client"""
    def __init__(self, config: TestConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.session.timeout = config.get('test_settings.timeout', 30)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Kaetram-API-Test/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def get(self, url: str, **kwargs) -> requests.Response:
        """Execute GET request"""
        self.logger.debug(f"GET {url}")
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Execute POST request"""
        self.logger.debug(f"POST {url}")
        return self.session.post(url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Execute PUT request"""
        self.logger.debug(f"PUT {url}")
        return self.session.put(url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Execute DELETE request"""
        self.logger.debug(f"DELETE {url}")
        return self.session.delete(url, **kwargs)

class TestResult:
    """Test result class"""
    def __init__(self, test_name: str, success: bool, message: str, data: Any = None, duration: float = 0):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.data = data
        self.duration = duration
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_name': self.test_name,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat()
        }

class TestSuite:
    """Test suite class"""
    def __init__(self, suite_name: str, config: TestConfig):
        self.suite_name = suite_name
        self.config = config
        self.logger = Logger(config)
        self.client = APIClient(config, self.logger)
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test"""
        self.logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=True,
                message="Test passed",
                data=result,
                duration=duration
            )
            self.logger.info(f"Test {test_name} passed in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                message=str(e),
                duration=duration
            )
            self.logger.error(f"Test {test_name} failed in {duration:.2f}s: {e}")
        
        self.results.append(test_result)
        return test_result
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        if not self.start_time:
            return {}
        
        total_duration = (self.end_time - self.start_time) if self.end_time else 0
        passed_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        report = {
            'suite_name': self.suite_name,
            'total_tests': len(self.results),
            'passed_tests': len(passed_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(passed_tests) / len(self.results) * 100 if self.results else 0,
            'total_duration': total_duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'results': [r.to_dict() for r in self.results]
        }
        
        return report
    
    def save_report(self, output_file: str = None):
        """Save test report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"test_reports/{self.suite_name}_{timestamp}.json"
        
        # Create directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Test report saved to {output_file}")
    
    def print_summary(self):
        """Print test summary"""
        if not self.results:
            print("No tests have been run")
            return
        
        report = self.generate_report()
        
        print(f"\n{'='*60}")
        print(f"Test Suite: {self.suite_name}")
        print(f"{'='*60}")
        
        # Summary table
        headers = ['Test Name', 'Status', 'Duration', 'Message']
        table_data = []
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            duration = f"{result.duration:.2f}s"
            message = result.message[:50] + "..." if len(result.message) > 50 else result.message
            table_data.append([result.test_name, status, duration, message])
        
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Summary statistics
        print(f"\nSummary:")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Failed: {report['failed_tests']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        print(f"Total Duration: {report['total_duration']:.2f}s")

# Utility functions
def validate_response(response: requests.Response) -> Dict[str, Any]:
    """Validate HTTP response"""
    if response.status_code != 200:
        raise ValueError(f"HTTP {response.status_code}: {response.text}")
    
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON response: {response.text}")

def generate_test_username(prefix: str = "test") -> str:
    """Generate test username"""
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}"

def cleanup_test_agents(config: TestConfig, tokens: List[str]):
    """Clean up test agents"""
    if not tokens:
        return
    
    logger = Logger(config)
    client = APIClient(config, logger)
    base_url = config.get('server.base_url')
    
    for token in tokens:
        try:
            response = client.post(f"{base_url}/ai/logout", json={'token': token})
            if response.status_code == 200:
                logger.info(f"Successfully logged out token: {token[:10]}...")
            else:
                logger.warning(f"Failed to logout token: {token[:10]}...")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def retry_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))

def wait_for_condition(condition, timeout: float = 10.0, interval: float = 0.5):
    """Wait for condition to be true"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    return False 