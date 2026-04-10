import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

# Mock settings if needed, or just import
try:
    from myproject.auth_service.app.messaging.publisher import publisher
    print("Testing RabbitMQ Publisher with current settings...")
    
    user_data = {
        "user_id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "action": "registration"
    }
    
    # This should NOT crash now, even if RabbitMQ is down
    publisher.publish_user_registered(user_data)
    print("Test completed successfully (no crash).")
except Exception as e:
    print(f"Test failed with error: {e}")
    sys.exit(1)
