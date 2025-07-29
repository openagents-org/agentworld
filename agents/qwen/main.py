"""
Main entry point for Qwen AI Agent for Kaetram Game
"""

import sys
import os
import argparse
import time
from qwen_agent import QwenAgent
from config import DASHSCOPE_API_KEY


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   Qwen AI Agent for Kaetram                 ║
    ║                                                              ║
    ║    An intelligent AI agent that plays Kaetram MMORPG        ║
    ║    using Alibaba Cloud Qwen Function Calling                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Check if environment is properly configured"""
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-dashscope-api-key":
        print("❌ Error: DASHSCOPE_API_KEY not configured!")
        print("Please set your Dashscope API key in environment variable:")
        print("export DASHSCOPE_API_KEY=your-actual-api-key")
        print("\nOr modify the config.py file.")
        return False
    
    print("✅ Environment check passed")
    return True


def interactive_mode():
    """Run agent in interactive mode"""
    print("\n🎮 Starting Interactive Mode")
    print("Type 'quit' to exit, 'reset' to reset conversation, 'auto' to start auto-play")
    print("=" * 60)
    
    agent = QwenAgent()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                print("🔄 Conversation reset")
                continue
            elif user_input.lower() == 'auto':
                print("🤖 Starting auto-play mode...")
                responses = agent.auto_play(7)
                for response in responses:
                    print(f"\n🤖 Agent: {response}")
                    print("-" * 60)
                continue
            elif user_input.lower() == 'start':
                print("🎮 Starting game session...")
                response = agent.start_game_session()
                print(f"\n🤖 Agent: {response}")
                continue
            elif not user_input:
                continue
            
            print("🤖 Agent: Processing...")
            response = agent.process_user_input(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def auto_play_mode(steps: int = 10):
    """Run agent in auto-play mode"""
    print(f"\n🤖 Starting Auto-Play Mode ({steps} steps)")
    print("=" * 60)
    
    agent = QwenAgent()
    
    try:
        responses = agent.auto_play(steps)
        
        for i, response in enumerate(responses):
            print(f"\n📝 Step {i}: {response}")
            print("-" * 60)
            time.sleep(1)
        
        print("\n✅ Auto-play completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Auto-play interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during auto-play: {str(e)}")


def test_connection():
    """Test connection to game server and AI model"""
    print("\n🔧 Testing Connections...")
    print("=" * 60)
    
    # Test game server connection
    print("🎮 Testing Kaetram game server connection...")
    try:
        import requests
        from config import KAETRAM_BASE_URL
        
        response = requests.get(f"{KAETRAM_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Game server connection successful")
            server_info = response.json()
            print(f"   Server: {server_info.get('name', 'Unknown')}")
            print(f"   Players: {server_info.get('playerCount', 0)}/{server_info.get('maxPlayers', 'Unknown')}")
        else:
            print(f"❌ Game server returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Game server connection failed: {str(e)}")
        print("   Make sure Kaetram server is running on http://localhost:9002")
    
    # Test AI model connection
    print("\n🧠 Testing Qwen AI model connection...")
    try:
        agent = QwenAgent()
        response = agent.process_user_input("Hello, can you hear me?")
        if response and not response.startswith("Error:"):
            print("✅ AI model connection successful")
            print(f"   Response: {response[:100]}...")
        else:
            print(f"❌ AI model connection failed: {response}")
    except Exception as e:
        print(f"❌ AI model connection failed: {str(e)}")
    
    print("\n✅ Connection test completed")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Qwen AI Agent for Kaetram Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive mode
  python main.py --auto             # Auto-play mode (10 steps)
  python main.py --auto --steps 20  # Auto-play mode (20 steps)
  python main.py --test             # Test connections
        """
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in auto-play mode"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        default=10,
        help="Number of auto-play steps (default: 10)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test connections to game server and AI model"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run based on mode
    if args.test:
        test_connection()
    elif args.auto:
        auto_play_mode(args.steps)
    else:
        interactive_mode()


if __name__ == "__main__":
    main() 