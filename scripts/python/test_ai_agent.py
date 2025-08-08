#!/usr/bin/env python3
"""
Kaetram AI Agent Complete Workflow Test
Simulates real game flows
"""
import os
import sys
import time
import random
from typing import Dict, List, Optional, Any

# Add utils path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from test_utils import TestConfig, TestSuite, validate_response, cleanup_test_agents, generate_test_username

class AIAgentFlowTests:
    def __init__(self, config: TestConfig):
        self.config = config
        self.suite = TestSuite("AIAgentFlow", config)
        self.base_url = config.get('server.base_url')
        self.test_tokens = []
        self.agent_data = {}
        
    def test_agent_lifecycle(self) -> Dict[str, Any]:
        """Test complete AI agent lifecycle"""
        # 1. Create agent
        username = generate_test_username("flow_test")
        password = "testpass123"
        
        # Create agent
        response = self.suite.client.post(f"{self.base_url}/ai/create", json={
            "username": username,
            "password": password
        })
        create_data = validate_response(response)
        
        if create_data.get('status') != 'success':
            raise ValueError(f"Agent creation failed: {create_data.get('message')}")
        
        # 2. Login
        response = self.suite.client.post(f"{self.base_url}/ai/login", json={
            "username": username,
            "password": password
        })
        login_data = validate_response(response)
        
        if login_data.get('status') != 'success':
            raise ValueError(f"Login failed: {login_data.get('message')}")
        
        token = login_data['token']
        self.test_tokens.append(token)
        
        # 3. Get initial observation
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        # 4. Send greeting message
        response = self.suite.client.post(f"{self.base_url}/ai/chat", json={
            "token": token,
            "message": "Hello! I'm starting my adventure!"
        })
        chat_data = validate_response(response)
        
        # 5. Move to a new location
        response = self.suite.client.post(f"{self.base_url}/ai/move", json={
            "token": token,
            "x": 150,
            "y": 150
        })
        move_data = validate_response(response)
        
        # 6. Logout
        response = self.suite.client.post(f"{self.base_url}/ai/logout", json={
            "token": token
        })
        logout_data = validate_response(response)
        
        if logout_data.get('status') != 'success':
            raise ValueError(f"Logout failed: {logout_data.get('message')}")
        
        # Remove token from cleanup list
        if token in self.test_tokens:
            self.test_tokens.remove(token)
        
        return {
            "username": username,
            "steps_completed": 6,
            "initial_location": observe_data.get('location'),
            "final_status": "logged_out"
        }
    
    def test_exploration_workflow(self) -> Dict[str, Any]:
        """Test exploration and movement workflow"""
        # 1. Login first
        login_data = self._create_and_login("explorer")
        token = login_data['token']
        
        # 2. Get initial position
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        initial_location = observe_data.get('location', {})
        
        # 3. Explore multiple locations
        exploration_points = [
            {"x": 200, "y": 200},
            {"x": 100, "y": 300},
            {"x": 250, "y": 150},
            {"x": 180, "y": 250}
        ]
        
        visited_locations = []
        for point in exploration_points:
            # Move to location
            response = self.suite.client.post(f"{self.base_url}/ai/move", json={
                "token": token,
                "x": point['x'],
                "y": point['y']
            })
            move_data = validate_response(response)
            
            # Wait a bit for movement
            time.sleep(0.5)
            
            # Observe the new location
            response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
                "token": token
            })
            observe_data = validate_response(response)
            
            visited_locations.append({
                "target": point,
                "observed": observe_data.get('location', {}),
                "entities": len(observe_data.get('entities', [])),
                "timestamp": time.time()
            })
        
        return {
            "initial_location": initial_location,
            "visited_locations": visited_locations,
            "total_moves": len(exploration_points)
        }
    
    def test_combat_workflow(self) -> Dict[str, Any]:
        """Test combat workflow"""
        # 1. Login first
        login_data = self._create_and_login("warrior")
        token = login_data['token']
        
        # 2. Look for enemies
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        entities = observe_data.get('entities', [])
        enemies = [e for e in entities if e.get('type') == 'mob']
        
        combat_actions = []
        
        if enemies:
            # Try to attack first enemy
            enemy = enemies[0]
            response = self.suite.client.post(f"{self.base_url}/ai/attack", json={
                "token": token,
                "target": enemy.get('instance', 'test_target')
            })
            
            # This might fail if the enemy is too far or doesn't exist
            try:
                attack_data = validate_response(response)
                combat_actions.append({
                    "action": "attack",
                    "target": enemy.get('name', 'unknown'),
                    "result": "attempted"
                })
            except:
                combat_actions.append({
                    "action": "attack",
                    "target": enemy.get('name', 'unknown'),
                    "result": "failed"
                })
        
        # Test stop combat
        response = self.suite.client.post(f"{self.base_url}/ai/stop", json={
            "token": token
        })
        stop_data = validate_response(response)
        
        combat_actions.append({
            "action": "stop",
            "result": "success" if stop_data.get('status') == 'success' else "failed"
        })
        
        return {
            "enemies_found": len(enemies),
            "combat_actions": combat_actions,
            "final_status": "combat_stopped"
        }
    
    def test_resource_gathering_workflow(self) -> Dict[str, Any]:
        """Test resource gathering workflow"""
        # 1. Login first
        login_data = self._create_and_login("gatherer")
        token = login_data['token']
        
        # 2. Look for resources
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        entities = observe_data.get('entities', [])
        resources = [e for e in entities if e.get('type') == 'resource']
        
        gathering_actions = []
        
        if resources:
            # Try to collect first resource
            resource = resources[0]
            response = self.suite.client.post(f"{self.base_url}/ai/collect", json={
                "token": token,
                "resource": resource.get('instance', 'test_resource')
            })
            
            # This might fail if the resource is too far or doesn't exist
            try:
                collect_data = validate_response(response)
                gathering_actions.append({
                    "action": "collect",
                    "resource": resource.get('name', 'unknown'),
                    "result": "attempted"
                })
            except:
                gathering_actions.append({
                    "action": "collect",
                    "resource": resource.get('name', 'unknown'),
                    "result": "failed"
                })
        
        # Test crafting with any available materials
        response = self.suite.client.post(f"{self.base_url}/ai/craft", json={
            "token": token,
            "item": "test_item"
        })
        
        try:
            craft_data = validate_response(response)
            gathering_actions.append({
                "action": "craft",
                "item": "test_item",
                "result": "attempted"
            })
        except:
            gathering_actions.append({
                "action": "craft",
                "item": "test_item",
                "result": "failed"
            })
        
        return {
            "resources_found": len(resources),
            "gathering_actions": gathering_actions,
            "final_status": "gathering_complete"
        }
    
    def test_equipment_workflow(self) -> Dict[str, Any]:
        """Test equipment management workflow"""
        # 1. Login first
        login_data = self._create_and_login("adventurer")
        token = login_data['token']
        
        # 2. Check initial inventory
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        initial_inventory = observe_data.get('inventory', {})
        
        # 3. Try to equip items from inventory
        equipment_actions = []
        
        # Try equipping from different inventory slots
        for slot in range(5):  # Try first 5 slots
            response = self.suite.client.post(f"{self.base_url}/ai/equip", json={
                "token": token,
                "index": slot
            })
            
            try:
                equip_data = validate_response(response)
                equipment_actions.append({
                    "action": "equip",
                    "slot": slot,
                    "result": "attempted"
                })
            except:
                equipment_actions.append({
                    "action": "equip",
                    "slot": slot,
                    "result": "failed"
                })
        
        # 4. Check final inventory state
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        final_inventory = observe_data.get('inventory', {})
        
        return {
            "initial_inventory": initial_inventory,
            "equipment_actions": equipment_actions,
            "final_inventory": final_inventory,
            "total_equip_attempts": len(equipment_actions)
        }
    
    def test_social_interaction_workflow(self) -> Dict[str, Any]:
        """Test social interaction workflow"""
        # 1. Login first
        login_data = self._create_and_login("socialite")
        token = login_data['token']
        
        # 2. Send various types of messages
        messages = [
            "Hello everyone!",
            "How is everyone doing today?",
            "This is a great game!",
            "Anyone want to team up?",
            "Good luck with your adventures!"
        ]
        
        chat_actions = []
        
        for message in messages:
            response = self.suite.client.post(f"{self.base_url}/ai/chat", json={
                "token": token,
                "message": message
            })
            
            try:
                chat_data = validate_response(response)
                chat_actions.append({
                    "message": message,
                    "result": "sent",
                    "timestamp": time.time()
                })
            except Exception as e:
                chat_actions.append({
                    "message": message,
                    "result": "failed",
                    "error": str(e)
                })
            
            # Wait between messages
            time.sleep(0.5)
        
        # 3. Try to observe other players
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        
        entities = observe_data.get('entities', [])
        players = [e for e in entities if e.get('type') == 'player']
        
        return {
            "chat_actions": chat_actions,
            "messages_sent": len([a for a in chat_actions if a['result'] == 'sent']),
            "players_observed": len(players),
            "final_status": "social_interaction_complete"
        }
    
    def test_full_game_session(self) -> Dict[str, Any]:
        """Test complete game session workflow"""
        # 1. Create and login
        login_data = self._create_and_login("complete_player")
        token = login_data['token']
        
        session_log = []
        
        # 2. Initial observation
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        observe_data = validate_response(response)
        session_log.append({"action": "observe", "timestamp": time.time()})
        
        # 3. Say hello
        response = self.suite.client.post(f"{self.base_url}/ai/chat", json={
            "token": token,
            "message": "Starting my complete game session!"
        })
        session_log.append({"action": "chat", "timestamp": time.time()})
        
        # 4. Move around
        for i in range(3):
            x = 100 + i * 50
            y = 100 + i * 50
            response = self.suite.client.post(f"{self.base_url}/ai/move", json={
                "token": token,
                "x": x,
                "y": y
            })
            session_log.append({"action": "move", "coordinates": [x, y], "timestamp": time.time()})
            time.sleep(0.5)
        
        # 5. Try some actions
        actions = [
            {"endpoint": "attack", "data": {"target": "test_target"}},
            {"endpoint": "collect", "data": {"resource": "test_resource"}},
            {"endpoint": "craft", "data": {"item": "test_item"}},
            {"endpoint": "equip", "data": {"index": 0}},
            {"endpoint": "stop", "data": {}},
        ]
        
        for action in actions:
            try:
                response = self.suite.client.post(f"{self.base_url}/ai/{action['endpoint']}", json={
                    "token": token,
                    **action['data']
                })
                session_log.append({
                    "action": action['endpoint'],
                    "result": "attempted",
                    "timestamp": time.time()
                })
            except:
                session_log.append({
                    "action": action['endpoint'],
                    "result": "failed",
                    "timestamp": time.time()
                })
        
        # 6. Final observation
        response = self.suite.client.get(f"{self.base_url}/ai/observe", params={
            "token": token
        })
        final_observe = validate_response(response)
        session_log.append({"action": "final_observe", "timestamp": time.time()})
        
        # 7. Say goodbye
        response = self.suite.client.post(f"{self.base_url}/ai/chat", json={
            "token": token,
            "message": "Ending my session. Thanks for playing!"
        })
        session_log.append({"action": "goodbye", "timestamp": time.time()})
        
        return {
            "session_duration": session_log[-1]['timestamp'] - session_log[0]['timestamp'],
            "total_actions": len(session_log),
            "actions_performed": [log['action'] for log in session_log],
            "final_location": final_observe.get('location'),
            "session_complete": True
        }
    
    def _create_and_login(self, prefix: str) -> Dict[str, Any]:
        """Helper method to create and login agent"""
        username = generate_test_username(prefix)
        password = "testpass123"
        
        # Create agent
        response = self.suite.client.post(f"{self.base_url}/ai/create", json={
            "username": username,
            "password": password
        })
        create_data = validate_response(response)
        
        if create_data.get('status') != 'success':
            raise ValueError(f"Agent creation failed: {create_data.get('message')}")
        
        # Login
        response = self.suite.client.post(f"{self.base_url}/ai/login", json={
            "username": username,
            "password": password
        })
        login_data = validate_response(response)
        
        if login_data.get('status') != 'success':
            raise ValueError(f"Login failed: {login_data.get('message')}")
        
        self.test_tokens.append(login_data['token'])
        self.agent_data[username] = {
            "username": username,
            "password": password,
            "token": login_data['token'],
            "created_at": time.time()
        }
        
        return login_data
    
    def run_all_tests(self):
        """Run all tests"""
        self.suite.start_time = time.time()
        
        # Define test methods
        test_methods = [
            ("agent_lifecycle", self.test_agent_lifecycle),
            ("exploration_workflow", self.test_exploration_workflow),
            ("combat_workflow", self.test_combat_workflow),
            ("resource_gathering_workflow", self.test_resource_gathering_workflow),
            ("equipment_workflow", self.test_equipment_workflow),
            ("social_interaction_workflow", self.test_social_interaction_workflow),
            ("full_game_session", self.test_full_game_session),
        ]
        
        # Run each test
        for test_name, test_func in test_methods:
            try:
                self.suite.run_test(test_name, test_func)
                # Small delay between tests
                time.sleep(1)
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
        tests = AIAgentFlowTests(config)
        tests.run_all_tests()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 