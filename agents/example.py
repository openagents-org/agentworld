"""
Example script demonstrating how to use the Qwen AI Agent for Kaetram
"""

import time
from qwen_agent import QwenAgent
from config import DASHSCOPE_API_KEY


def basic_usage_example():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Check if API key is configured
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-dashscope-api-key":
        print("Error: Please configure DASHSCOPE_API_KEY first!")
        return
    
    # Create agent instance
    agent = QwenAgent()
    
    # Start game session
    print("\n1. Starting game session...")
    response = agent.start_game_session()
    print(f"Response: {response}")
    
    # Give some basic instructions
    instructions = [
        "Look around and tell me what you see in the environment",
        "Move to coordinates 100, 100 to explore a new area", 
        "Send a chat message saying 'Hello fellow adventurers!'",
        "If you see any resources like trees or rocks, try to collect them"
    ]
    
    for i, instruction in enumerate(instructions, 2):
        print(f"\n{i}. Instruction: {instruction}")
        response = agent.process_user_input(instruction)
        print(f"Response: {response}")
        time.sleep(2)  # Brief pause between actions


def auto_play_example():
    """Auto-play example"""
    print("\n\n=== Auto-Play Example ===")
    
    agent = QwenAgent()
    
    print("Starting auto-play for 5 steps...")
    responses = agent.auto_play(steps=5)
    
    for response in responses:
        print(f"\n{response}")
        print("-" * 50)


def interactive_conversation_example():
    """Interactive conversation example"""
    print("\n\n=== Interactive Conversation Example ===")
    
    agent = QwenAgent()
    
    # Simulate a conversation
    conversation = [
        "Hello! I want you to start playing Kaetram",
        "First, observe your surroundings and tell me about the game world",
        "Now try to find some interesting places to explore",
        "If you encounter any other players, be friendly and say hello"
    ]
    
    for user_input in conversation:
        print(f"\nUser: {user_input}")
        response = agent.process_user_input(user_input)
        print(f"Agent: {response}")
        time.sleep(1)


def custom_game_strategy_example():
    """Example of custom game strategy"""
    print("\n\n=== Custom Game Strategy Example ===")
    
    agent = QwenAgent()
    
    # Login first
    agent.start_game_session()
    
    # Implement a resource gathering strategy
    strategy_steps = [
        "Observe the environment with a large radius to get a complete view",
        "Look for resources like trees, rocks, or fishing spots in your observations",
        "Move closer to the nearest resource you found",
        "Collect the resource using the appropriate skill",
        "After collecting, look for more resources in the area",
        "If you get attacked by enemies, defend yourself",
        "Send a chat message about your resource gathering progress"
    ]
    
    for step in strategy_steps:
        print(f"\nStrategy Step: {step}")
        response = agent.process_user_input(step)
        print(f"Result: {response}")
        time.sleep(3)



def test_all_game_functions():
    """Test all available game functions"""
    print("\n\n=== Testing All Game Functions ===")
    
    agent = QwenAgent()
    
    # Test each function individually
    test_cases = [
        "Create or login to a character named 'TestAgent'",
        "Observe your environment to see what's around you",
        "Move to coordinates 50, 50",
        "Send a chat message saying 'Testing AI agent functions'",
        "Try to equip any item from inventory slot 0 if available",
        "Look for any portals or warp points nearby and enter one if found",
        "Stop all current actions",
        "Search for resources and try to collect them",
        "Look for enemies and engage in combat if safe to do so"
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case}")
        try:
            response = agent.process_user_input(test_case)
            print(f"✅ Success: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        time.sleep(2)


def main():
    """Run all examples"""
    print("Qwen AI Agent for Kaetram - Examples")
    print("=" * 50)
    
    try:
        # Run basic example
        basic_usage_example()
        
        # Wait before next example
        time.sleep(3)
        
        # Run auto-play example
        auto_play_example()
        
        # Wait before next example  
        time.sleep(3)
        
        # Run interactive example
        interactive_conversation_example()
        
        # Wait before next example
        time.sleep(3)
        

        
        print("\n\n✅ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")


if __name__ == "__main__":
    main() 