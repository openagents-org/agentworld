#!/usr/bin/env python3
"""
Kaetram Hub API Test Script
"""
import os
import sys
import time
from typing import Dict, List, Optional, Any

# Add utils path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from test_utils import TestConfig, TestSuite, validate_response

class HubAPITests:
    def __init__(self, config: TestConfig):
        self.config = config
        self.suite = TestSuite("HubAPI", config)
        self.base_url = config.get('hub.base_url')
        self.access_token = config.get('hub.access_token')
        
    def test_hub_status(self) -> Dict[str, Any]:
        """Test Hub status"""
        response = self.suite.client.get(f"{self.base_url}/")
        data = validate_response(response)
        
        if 'status' not in data:
            raise ValueError("Missing status field in response")
        
        return data
    
    def test_get_server(self) -> Dict[str, Any]:
        """Test getting available server"""
        response = self.suite.client.get(f"{self.base_url}/server")
        data = validate_response(response)
        
        # May return error status (if no servers available)
        if data.get('status') == 'error':
            return {"message": "No servers available", "data": data}
        
        # Validate server info fields
        required_fields = ['id', 'name', 'host', 'port', 'players', 'maxPlayers']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return data
    
    def test_get_all_servers(self) -> Dict[str, Any]:
        """Test getting all servers"""
        response = self.suite.client.get(f"{self.base_url}/all")
        data = validate_response(response)
        
        # Should return a list of servers
        if not isinstance(data, list):
            raise ValueError("Expected list of servers")
        
        # If servers exist, validate their structure
        for server in data:
            required_fields = ['id', 'name', 'host', 'port', 'players', 'maxPlayers']
            for field in required_fields:
                if field not in server:
                    raise ValueError(f"Missing required field in server: {field}")
        
        return {"servers": data, "count": len(data)}
    
    def test_player_online_status(self) -> Dict[str, Any]:
        """Test player online status check"""
        if not self.access_token:
            return {"message": "No access token configured, skipping test"}
        
        # Test with a known player name
        test_player = "test_player"
        
        response = self.suite.client.post(f"{self.base_url}/isOnline", json={
            "username": test_player,
            "access_token": self.access_token
        })
        data = validate_response(response)
        
        # Should return boolean online status
        if 'online' not in data:
            raise ValueError("Missing online field in response")
        
        if not isinstance(data['online'], bool):
            raise ValueError("Online field should be boolean")
        
        return {"player": test_player, "online": data['online']}
    
    def test_leaderboards(self) -> Dict[str, Any]:
        """Test leaderboards endpoint"""
        response = self.suite.client.get(f"{self.base_url}/leaderboards")
        data = validate_response(response)
        
        # Should return leaderboard data
        if not isinstance(data, dict):
            raise ValueError("Expected leaderboard data object")
        
        # Check for standard leaderboard categories
        expected_categories = ['totalExperience', 'combat', 'skills']
        for category in expected_categories:
            if category not in data:
                self.suite.logger.warning(f"Missing leaderboard category: {category}")
        
        return data
    
    def test_skill_leaderboard(self) -> Dict[str, Any]:
        """Test skill-specific leaderboard"""
        skills = ['attack', 'defense', 'health', 'archery', 'magic']
        
        results = {}
        for skill in skills:
            try:
                response = self.suite.client.get(f"{self.base_url}/leaderboards", params={
                    "skill": skill
                })
                data = validate_response(response)
                
                # Should return list of players
                if not isinstance(data, list):
                    raise ValueError(f"Expected list for skill {skill}")
                
                results[skill] = {"count": len(data), "players": data[:5]}  # Store top 5
                
            except Exception as e:
                self.suite.logger.warning(f"Failed to get {skill} leaderboard: {e}")
                results[skill] = {"error": str(e)}
        
        return results
    
    def test_pvp_leaderboard(self) -> Dict[str, Any]:
        """Test PvP leaderboard"""
        response = self.suite.client.get(f"{self.base_url}/leaderboards", params={
            "pvp": "true"
        })
        data = validate_response(response)
        
        # Should return list of players
        if not isinstance(data, list):
            raise ValueError("Expected list for PvP leaderboard")
        
        # Validate player data structure
        for player in data[:5]:  # Check first 5 players
            if 'username' not in player:
                raise ValueError("Missing username in player data")
            if 'kills' not in player:
                raise ValueError("Missing kills in player data")
        
        return {"count": len(data), "top_players": data[:5]}
    
    def test_mob_leaderboard(self) -> Dict[str, Any]:
        """Test mob kill leaderboard"""
        mobs = ['rat', 'skeleton', 'ogre', 'spider']
        
        results = {}
        for mob in mobs:
            try:
                response = self.suite.client.get(f"{self.base_url}/leaderboards", params={
                    "mob": mob
                })
                data = validate_response(response)
                
                # Should return list of players
                if not isinstance(data, list):
                    raise ValueError(f"Expected list for mob {mob}")
                
                results[mob] = {"count": len(data), "players": data[:5]}  # Store top 5
                
            except Exception as e:
                self.suite.logger.warning(f"Failed to get {mob} leaderboard: {e}")
                results[mob] = {"error": str(e)}
        
        return results
    
    def test_password_reset_request(self) -> Dict[str, Any]:
        """Test password reset request"""
        test_email = "test@example.com"
        
        response = self.suite.client.post(f"{self.base_url}/api/v1/requestReset", json={
            "email": test_email
        })
        data = validate_response(response)
        
        # Should return success status
        if data.get('status') != 'success':
            # This is expected for test email, so just return the response
            return {"message": "Password reset request processed", "data": data}
        
        return data
    
    def test_password_reset(self) -> Dict[str, Any]:
        """Test password reset with token"""
        # Use dummy token for testing
        test_token = "test_reset_token"
        
        response = self.suite.client.post(f"{self.base_url}/api/v1/resetPassword", json={
            "token": test_token,
            "password": "newpassword123"
        })
        data = validate_response(response)
        
        # Should return error for invalid token (expected)
        if data.get('status') == 'error':
            return {"message": "Invalid token (expected)", "data": data}
        
        return data
    
    def test_stripe_webhook(self) -> Dict[str, Any]:
        """Test Stripe webhook endpoint (if configured)"""
        stripe_endpoint = self.config.get('hub.stripe_endpoint')
        
        if not stripe_endpoint:
            return {"message": "No Stripe endpoint configured, skipping test"}
        
        # Test webhook endpoint with dummy payload
        response = self.suite.client.post(f"{self.base_url}/{stripe_endpoint}", json={
            "type": "test.event",
            "data": {"object": {"id": "test_payment"}}
        })
        
        # This will likely fail without proper Stripe signature, which is expected
        if response.status_code != 200:
            return {"message": "Stripe webhook test (expected to fail without signature)", "status": response.status_code}
        
        return {"message": "Stripe webhook responded successfully"}
    
    def run_all_tests(self):
        """Run all tests"""
        self.suite.start_time = time.time()
        
        # Define test methods
        test_methods = [
            ("hub_status", self.test_hub_status),
            ("get_server", self.test_get_server),
            ("get_all_servers", self.test_get_all_servers),
            ("player_online_status", self.test_player_online_status),
            ("leaderboards", self.test_leaderboards),
            ("skill_leaderboard", self.test_skill_leaderboard),
            ("pvp_leaderboard", self.test_pvp_leaderboard),
            ("mob_leaderboard", self.test_mob_leaderboard),
            ("password_reset_request", self.test_password_reset_request),
            ("password_reset", self.test_password_reset),
            ("stripe_webhook", self.test_stripe_webhook),
        ]
        
        # Run each test
        for test_name, test_func in test_methods:
            try:
                self.suite.run_test(test_name, test_func)
            except Exception as e:
                self.suite.logger.error(f"Error running test {test_name}: {e}")
        
        self.suite.end_time = time.time()
        
        # Generate report
        self.suite.save_report()
        self.suite.print_summary()

def main():
    """Main function"""
    try:
        config = TestConfig()
        tests = HubAPITests(config)
        tests.run_all_tests()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 