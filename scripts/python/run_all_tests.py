#!/usr/bin/env python3
"""
Kaetram API Test Main Runner
"""
import os
import sys
import time
import argparse
from typing import List, Dict, Any

# Add utils path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from test_utils import TestConfig, Logger
from test_server_api import ServerAPITests
from test_hub_api import HubAPITests
from test_ai_agent import AIAgentFlowTests

def run_server_tests(config: TestConfig) -> Dict[str, Any]:
    """Run game server tests"""
    tests = ServerAPITests(config)
    tests.run_all_tests()
    return {
        "suite_name": "ServerAPI",
        "total_tests": len(tests.suite.results),
        "passed_tests": sum(1 for r in tests.suite.results if r.success),
        "failed_tests": sum(1 for r in tests.suite.results if not r.success),
        "duration": tests.suite.end_time - tests.suite.start_time if tests.suite.end_time else 0
    }

def run_hub_tests(config: TestConfig) -> Dict[str, Any]:
    """Run Hub tests"""
    tests = HubAPITests(config)
    tests.run_all_tests()
    return {
        "suite_name": "HubAPI",
        "total_tests": len(tests.suite.results),
        "passed_tests": sum(1 for r in tests.suite.results if r.success),
        "failed_tests": sum(1 for r in tests.suite.results if not r.success),
        "duration": tests.suite.end_time - tests.suite.start_time if tests.suite.end_time else 0
    }

def run_ai_agent_tests(config: TestConfig) -> Dict[str, Any]:
    """Run AI agent workflow tests"""
    tests = AIAgentFlowTests(config)
    tests.run_all_tests()
    return {
        "suite_name": "AIAgentFlow",
        "total_tests": len(tests.suite.results),
        "passed_tests": sum(1 for r in tests.suite.results if r.success),
        "failed_tests": sum(1 for r in tests.suite.results if not r.success),
        "duration": tests.suite.end_time - tests.suite.start_time if tests.suite.end_time else 0
    }

def print_summary(results: List[Dict[str, Any]], total_duration: float):
    """Print test summary"""
    print("\n" + "="*80)
    print("🎮 Kaetram API Test Summary")
    print("="*80)
    
    total_tests = sum(r['total_tests'] for r in results)
    total_passed = sum(r['passed_tests'] for r in results)
    total_failed = sum(r['failed_tests'] for r in results)
    
    for result in results:
        suite_name = result['suite_name'].ljust(20)
        status = "✅ PASSED" if result['failed_tests'] == 0 else "❌ FAILED"
        test_count = f"{result['passed_tests']}/{result['total_tests']}"
        duration = f"{result['duration']:.2f}s"
        
        print(f"{suite_name} | {status.ljust(9)} | {test_count.ljust(8)} | {duration.ljust(8)}")
    
    print("-"*80)
    total_status = "✅ PASSED" if total_failed == 0 else "❌ FAILED"
    total_count = f"{total_passed}/{total_tests}"
    total_dur = f"{total_duration:.2f}s"
    
    print(f"{'TOTAL'.ljust(20)} | {total_status.ljust(9)} | {total_count.ljust(8)} | {total_dur.ljust(8)}")
    
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} tests failed. Check the logs for details.")
    else:
        print(f"\n🎉 All tests passed! ({total_tests} tests)")
    
    print("="*80)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Kaetram API Test Runner")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--server", action="store_true", help="Run only server API tests")
    parser.add_argument("--hub", action="store_true", help="Run only Hub API tests")
    parser.add_argument("--ai", action="store_true", help="Run only AI agent workflow tests")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test data after execution")
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = TestConfig(args.config)
        logger = Logger(config)
        
        # Override config with command line args
        if args.verbose:
            logger.logger.setLevel("DEBUG")
        
        # Determine which tests to run
        run_server = args.server or not (args.hub or args.ai)
        run_hub = args.hub or not (args.server or args.ai)
        run_ai = args.ai or not (args.server or args.hub)
        
        # If specific tests are requested, only run those
        if args.server or args.hub or args.ai:
            run_server = args.server
            run_hub = args.hub
            run_ai = args.ai
        
        results = []
        start_time = time.time()
        
        print("🚀 Starting Kaetram API Tests")
        print(f"Configuration: {args.config}")
        print(f"Server URL: {config.get('server.base_url')}")
        print(f"Hub URL: {config.get('hub.base_url')}")
        print("-"*50)
        
        # Run tests
        if run_server:
            print("Running Server API Tests...")
            try:
                result = run_server_tests(config)
                results.append(result)
                logger.info(f"Server API tests completed: {result['passed_tests']}/{result['total_tests']} passed")
            except Exception as e:
                logger.error(f"Server API tests failed: {e}")
                results.append({
                    "suite_name": "ServerAPI",
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "duration": 0
                })
        
        if run_hub:
            print("Running Hub API Tests...")
            try:
                result = run_hub_tests(config)
                results.append(result)
                logger.info(f"Hub API tests completed: {result['passed_tests']}/{result['total_tests']} passed")
            except Exception as e:
                logger.error(f"Hub API tests failed: {e}")
                results.append({
                    "suite_name": "HubAPI",
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "duration": 0
                })
        
        if run_ai:
            print("Running AI Agent Workflow Tests...")
            try:
                result = run_ai_agent_tests(config)
                results.append(result)
                logger.info(f"AI Agent tests completed: {result['passed_tests']}/{result['total_tests']} passed")
            except Exception as e:
                logger.error(f"AI Agent tests failed: {e}")
                results.append({
                    "suite_name": "AIAgentFlow",
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "duration": 0
                })
        
        # Calculate total duration
        total_duration = time.time() - start_time
        
        # Print summary
        print_summary(results, total_duration)
        
        # Save combined report
        combined_report = {
            "timestamp": time.time(),
            "total_duration": total_duration,
            "suites": results,
            "summary": {
                "total_tests": sum(r['total_tests'] for r in results),
                "passed_tests": sum(r['passed_tests'] for r in results),
                "failed_tests": sum(r['failed_tests'] for r in results),
                "success_rate": (sum(r['passed_tests'] for r in results) / sum(r['total_tests'] for r in results) * 100) if sum(r['total_tests'] for r in results) > 0 else 0
            }
        }
        
        # Save report
        import json
        from pathlib import Path
        
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"combined_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(combined_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📊 Combined report saved to: {report_file}")
        
        # Exit with error code if any tests failed
        total_failed = sum(r['failed_tests'] for r in results)
        if total_failed > 0:
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 