import requests
import json

API_URL = "http://localhost:8000/api/honeypot"
API_KEY = "alterEgOI2345hCiGUvi_Buildathon"

# Test message
test_message = {
    "sessionId": "test-session-001",
    "message": {
        "sender": "customer",
        "text": "Your bank account will be blocked today. Verify immediately by sending your account number.",
        "timestamp": 1769776585000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "RMS",
        "language": "English",
        "locale": "IN"
    }
}

print("\n" + "="*70)
print("🧪 AI HONEYPOT SYSTEM TEST")
print("="*70)
print(f"\n📨 Incoming Scam Message:")
print(f"   \"{test_message['message']['text']}\"")
print("\n" + "-"*70)

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

try:
    response = requests.post(API_URL, json=test_message, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ HONEYPOT RESPONSE:")
        print("="*70)
        print(f"🎯 Scam Detected: {result['scam_detected']}")
        print(f"📊 Confidence Score: {result['confidence_score']*100}%")
        print(f"🤖 Agent Response: \"{result['agent_response']}\"")
        print(f"📈 Engagement Status: {result['engagement_status']}")
        print(f"🔄 Conversation Turns: {result['conversation_turns']}")
        print(f"⚠️  Threat Level: {result['threat_level'].upper()}")
        print(f"💬 Continue Conversation: {result['continue_conversation']}")
        
        print(f"\n🔍 Extracted Intelligence:")
        intel = result['extracted_intelligence']
        for key, values in intel.items():
            if values:
                print(f"   • {key}: {values}")
        if not any(intel.values()):
            print("   (None extracted yet - needs more conversation turns)")
        
        print("\n" + "="*70)
        print("✅ Test Complete - System Working!")
        print("="*70)
        
        # Save to file
        with open("test_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\n📁 Full response saved to: test_output.json\n")
        
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}\n")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to API")
    print("   Make sure server is running: python main.py\n")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}\n")