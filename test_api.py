import requests
import json

# Your local API URL
API_URL = "http://localhost:8000/detect-and-engage"

# Your API key (same as in .env file)
API_KEY = "alterEgO12345hClGUvi_Buildathon"

# Test scam messages
test_messages = [
    {
        "name": "Lottery Scam",
        "message": "Congratulations! You won ₹50,000. Send ₹500 to scammer@paytm to claim your prize!"
    },
    {
        "name": "Bank Phishing",
        "message": "Your bank account will be blocked! Update KYC immediately at http://fake-bank.com or call 9876543210"
    },
    {
        "name": "Job Scam",
        "message": "Work from home opportunity! Earn ₹5000 daily. Register now at http://scam-jobs.com. Contact: jobscam@gmail.com"
    },
    {
        "name": "Normal Message (Not Scam)",
        "message": "Hey, how are you doing today?"
    }
]

def test_api(message_data):
    """Test the honeypot API with a message"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {message_data['name']}")
    print(f"{'='*60}")
    print(f"Message: {message_data['message']}")
    print(f"-"*60)
    
    # Prepare request
    payload = {
        "conversation_id": "test_001",
        "message": message_data['message'],
        "conversation_history": []
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        # Send request
        response = requests.post(API_URL, json=payload, headers=headers)
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: SUCCESS")
            print(f"\nScam Detected: {result['scam_detected']}")
            print(f"Confidence: {result['confidence_score']:.2f}")
            print(f"Agent Response: {result['agent_response']}")
            print(f"Threat Level: {result['threat_level']}")
            print(f"\nExtracted Intelligence:")
            print(json.dumps(result['extracted_intelligence'], indent=2))
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is it running?")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

# Run tests
if __name__ == "__main__":
    print("\n🧪 HONEYPOT API LOCAL TESTING")
    print("="*60)
    
    for test_msg in test_messages:
        test_api(test_msg)
    
    print(f"\n{'='*60}")
    print("✅ Testing Complete!")
    print(f"{'='*60}\n")