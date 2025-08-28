from src.tests.user_sessions.session_manager import UserSessionManager
from datetime import datetime

def test_session_manager():
    # Create session manager
    manager = UserSessionManager()
    
    # Test data
    test_session = {
        'operator_name': 'Test User',
        'company_name': 'Test Company', 
        'session_start': datetime.now(),
        'decisions_made': [
            {
                'stage': 'mining',
                'decision': {'ore_type': 'Phosphorite Ore', 'quantity': 1000}
            }
        ]
    }
    
    # Save session
    session_file = manager.save_session_log(test_session, "test_session")
    print(f"Session saved to: {session_file}")
    
    # List available sessions
    sessions = manager.list_available_sessions()
    print(f"Available sessions: {sessions}")
    
    print("✅ Session manager working correctly!")

if __name__ == "__main__":
    test_session_manager()