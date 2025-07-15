#!/usr/bin/env python3
"""
Kaetram Game Server API Test Script
"""
import os
import sys
import time
import json
from typing import Dict, List, Optional, Any

# Add utils path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from test_utils import TestConfig, TestSuite, validate_response, cleanup_test_agents, generate_test_username

class ServerAPITests:
    def __init__(self, config: TestConfig):
        self.config = config
        self.suite = TestSuite("ServerAPI", config)
        self.base_url = config.get('server.base_url')
        self.test_tokens = []  # Save test tokens for cleanup
        
    def test_server_info(self) -> Dict[str, Any]:
        """Test server information endpoint"""
        response = self.suite.client.get(f"{self.base_url}/")
        data = validate_response(response)
        
        # Validate returned fields
        required_fields = ['name', 'port', 'gameVersion', 'maxPlayers', 'playerCount']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return data
    
    def test_ai_create_agent(self) -> Dict[str, Any]:
        """Test creating AI agent"""
        username = generate_test_username()
        password = "testpass123"
        
        response = self.suite.client.post(f"{self.base_url}/ai/create", json={
            "username": username,
            "password": password
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Agent creation failed: {data.get('message', 'Unknown error')}")
        
        if 'token' not in data:
            raise ValueError("Missing token field in response")
        
        # Save token for cleanup
        self.test_tokens.append(data['token'])
        
        return {"username": username, "password": password, "token": data['token']}
    
    def test_ai_login(self) -> Dict[str, Any]:
        """Test AI agent login"""
        # First create an agent
        agent_data = self.test_ai_create_agent()
        
        response = self.suite.client.post(f"{self.base_url}/ai/login", json={
            "username": agent_data['username'],
            "password": agent_data['password']
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Login failed: {data.get('message', 'Unknown error')}")
        
        if 'token' not in data:
            raise ValueError("Missing token field in response")
        
        # Update token
        self.test_tokens.append(data['token'])
        
        return {"token": data['token']}
    
    def test_ai_logout(self) -> Dict[str, Any]:
        """Test AI agent logout"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        response = self.suite.client.post(f"{self.base_url}/ai/logout", json={
            "token": token
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Logout failed: {data.get('message', 'Unknown error')}")
        
        # Remove token from cleanup list
        if token in self.test_tokens:
            self.test_tokens.remove(token)
        
        return data
    
    def test_ai_move(self) -> Dict[str, Any]:
        """Test AI agent movement"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test movement
        response = self.suite.client.post(f"{self.base_url}/ai/move", json={
            "token": token,
            "x": 100,
            "y": 100
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Movement failed: {data.get('message', 'Unknown error')}")
        
        return data
    
    def test_ai_stop(self) -> Dict[str, Any]:
        """Test AI agent stop"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test stop
        response = self.suite.client.post(f"{self.base_url}/ai/stop", json={
            "token": token
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Stop failed: {data.get('message', 'Unknown error')}")
        
        return data
    
    def test_ai_chat(self) -> Dict[str, Any]:
        """Test AI agent chat"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test chat
        response = self.suite.client.post(f"{self.base_url}/ai/chat", json={
            "token": token,
            "message": "Hello, this is a test message!"
        })
        data = validate_response(response)
        
        # Validate response
        if data.get('status') != 'success':
            raise ValueError(f"Chat failed: {data.get('message', 'Unknown error')}")
        
        return data
    
    def test_ai_observe(self) -> Dict[str, Any]:
        """Test AI agent observation"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test observe
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        data = validate_response(response)
        
        # Validate response structure
        expected_fields = ['location', 'map', 'entities', 'inventory', 'player']
        for field in expected_fields:
            if field not in data:
                raise ValueError(f"Missing expected field in observation: {field}")
        
        return data
    
    def test_ai_attack(self) -> Dict[str, Any]:
        """Test AI agent attack"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test attack (using a test target ID)
        response = self.suite.client.post(f"{self.base_url}/ai/attack", json={
            "token": token,
            "target": "test_target_id"
        })
        data = validate_response(response)
        
        # Attack may fail due to no target, but should still return valid response
        if data.get('status') not in ['success', 'error']:
            raise ValueError(f"Invalid attack response: {data}")
        
        return data
    
    def test_ai_equip(self) -> Dict[str, Any]:
        """Test AI agent equipment"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test equip (using a test item index)
        response = self.suite.client.post(f"{self.base_url}/ai/equip", json={
            "token": token,
            "index": 0
        })
        data = validate_response(response)
        
        # Equip may fail due to no item, but should still return valid response
        if data.get('status') not in ['success', 'error']:
            raise ValueError(f"Invalid equip response: {data}")
        
        return data
    
    def test_ai_collect(self) -> Dict[str, Any]:
        """Test AI agent resource collection"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test collect (using a test resource ID)
        response = self.suite.client.post(f"{self.base_url}/ai/collect", json={
            "token": token,
            "resource": "test_resource_id"
        })
        data = validate_response(response)
        
        # Collect may fail due to no resource, but should still return valid response
        if data.get('status') not in ['success', 'error']:
            raise ValueError(f"Invalid collect response: {data}")
        
        return data
    
    def test_ai_craft(self) -> Dict[str, Any]:
        """Test AI agent crafting"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test craft (using a test item key)
        response = self.suite.client.post(f"{self.base_url}/ai/craft", json={
            "token": token,
            "item": "test_item_key"
        })
        data = validate_response(response)
        
        # Craft may fail due to no materials, but should still return valid response
        if data.get('status') not in ['success', 'error']:
            raise ValueError(f"Invalid craft response: {data}")
        
        return data
    
    def test_ai_enter(self) -> Dict[str, Any]:
        """Test AI agent entering portals"""
        # First login
        login_data = self.test_ai_login()
        token = login_data['token']
        
        # Test enter (portal/warp)
        response = self.suite.client.post(f"{self.base_url}/ai/enter", json={
            "token": token
        })
        data = validate_response(response)
        
        # Enter may fail due to no portal, but should still return valid response
        if data.get('status') not in ['success', 'error']:
            raise ValueError(f"Invalid enter response: {data}")
        
        return data
    
    def run_all_tests(self):
        """Run all tests"""
        self.suite.start_time = time.time()
        
        # Define test methods
        test_methods = [
            ("server_info", self.test_server_info),
            ("ai_create_agent", self.test_ai_create_agent),
            ("ai_login", self.test_ai_login),
            ("ai_logout", self.test_ai_logout),
            ("ai_move", self.test_ai_move),
            ("ai_stop", self.test_ai_stop),
            ("ai_chat", self.test_ai_chat),
            ("ai_observe", self.test_ai_observe),
            ("ai_attack", self.test_ai_attack),
            ("ai_equip", self.test_ai_equip),
            ("ai_collect", self.test_ai_collect),
            ("ai_craft", self.test_ai_craft),
            ("ai_enter", self.test_ai_enter),
        ]
        
        # Run each test
        for test_name, test_func in test_methods:
            try:
                self.suite.run_test(test_name, test_func)
            except Exception as e:
                self.suite.logger.error(f"Error running test {test_name}: {e}")
        
        self.suite.end_time = time.time()
        
        # Cleanup
        if self.test_tokens:
            cleanup_test_agents(self.config, self.test_tokens)
        
        # Generate report
        self.suite.save_report()
        self.suite.print_summary()

def main():
    """Main function"""
    try:
        config = TestConfig()
        tests = ServerAPITests(config)
        tests.run_all_tests()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 