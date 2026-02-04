import requests
import json

# Your local API URL (UPDATED FOR GUVI)
API_URL = "http://localhost:8000/api/honeypot"

# Your API key (CORRECTED - matches the GUVI test interface)
API_KEY = "alterEgOI2345hCiGUvi_Buildathon"

# Test message matching GUVI format
test_message = {
    "sessionId": "IIc984e8-f4d4-47ee-850A-9aeb769592E7",
    "message": {
        "sender": "customer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": 1769776585000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "RMS",
        "language": "English",
        "locale": "IN"
    }
}

def test_api():
    """Test the honeypot API with GUVI format"""
    
    print(f"\n{'='*60}")
    print(f"Testing GUVI Honeypot Endpoint")
    print(f"{'='*60}")
    print(f"Message: {test_message['message']['text']}")
    print(f"-"*60)
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        # Send request
        response = requests.post(API_URL, json=test_message, headers=headers)
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: SUCCESS")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is it running?")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

# Run test
if __name__ == "__main__":
    print("\n🧪 GUVI HONEYPOT API LOCAL TESTING")
    print("="*60)
    
    test_api()
    
    print(f"\n{'='*60}")
    print("✅ Testing Complete!")
    print(f"{'='*60}\n")