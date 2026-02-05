from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import os
import re
import json
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

app = FastAPI(title="Honeypot Scam Detector")

# API Keys
MY_API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# DEBUG
print(f"DEBUG: Loaded API_KEY = {repr(MY_API_KEY)}")
print(f"DEBUG: Length = {len(MY_API_KEY) if MY_API_KEY else 0}")
print(f"DEBUG: Bytes = {MY_API_KEY.encode() if MY_API_KEY else b''}")

# Configure Gemini with new SDK
client = genai.Client(api_key=GEMINI_API_KEY)

# In-memory conversation store (use Redis/DB in production)
conversation_store = {}

# ===================== MODELS =====================

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int | float

class IncomingRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: list = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class HoneypotResponse(BaseModel):
    scam_detected: bool
    confidence_score: float
    agent_response: str
    engagement_status: str
    conversation_turns: int
    extracted_intelligence: Dict[str, List[str]]
    threat_level: str
    continue_conversation: bool

# ===================== AI FUNCTIONS =====================

def detect_scam_with_ai(message: str, history: list) -> dict:
    """Use Gemini to detect if message is a scam"""
    
    prompt = f"""Analyze if this message is a scam. Look for:
- Urgency/threats (account blocked, immediate action needed)
- Prize/lottery claims (you won, congratulations) 
- Requests for money, bank details, or personal info
- Phishing links or suspicious URLs
- Impersonation (bank, government, company)
- Job scams (work from home, easy money)
- OTP/verification code requests

Message: "{message}"

Return ONLY valid JSON in this exact format:
{{"is_scam": true/false, "confidence": 0.0-1.0, "scam_type": "phishing/lottery/job/bank/other/none"}}"""

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        return result
    except Exception as e:
        # Fallback to keyword-based detection
        scam_keywords = ['blocked', 'suspended', 'verify', 'won', 'prize', 'congratulations', 
                         'urgent', 'immediately', 'otp', 'bank account', 'upi', 'payment']
        text_lower = message.lower()
        scam_count = sum(1 for kw in scam_keywords if kw in text_lower)
        
        is_scam = scam_count >= 2
        confidence = min(scam_count / 5, 1.0) if is_scam else 0.2
        
        return {
            "is_scam": is_scam,
            "confidence": confidence,
            "scam_type": "phishing" if is_scam else "none"
        }

def generate_agent_response(message: str, scam_type: str, history: list, turn: int) -> str:
    """Generate believable agent response using Gemini"""
    
    # Build conversation context
    history_text = "\n".join([f"- {h.get('sender', 'unknown')}: {h.get('text', '')}" for h in history[-3:]])
    
    # Persona instructions based on scam type
    persona_instructions = {
        "phishing": "You're concerned about your account. Ask why it's blocked and what you need to do.",
        "lottery": "You're excited but confused. Ask how to claim the prize.",
        "job": "You're interested in the opportunity. Ask about job details and payment.",
        "bank": "You're worried about your bank account. Ask for clarification.",
        "other": "You're curious and concerned. Ask for more information."
    }
    
    instruction = persona_instructions.get(scam_type, persona_instructions["other"])
    
    prompt = f"""You are roleplaying as a believable potential scam victim. Your goal is to engage the scammer naturally to extract information.

CRITICAL RULES:
1. NEVER reveal you know it's a scam
2. Sound genuinely concerned, curious, or naive
3. Ask clarifying questions to get more details
4. Be conversational and natural
5. Keep responses SHORT (1-2 sentences max)
6. Match the tone - if they're urgent, be worried; if friendly, be curious

Scam type: {scam_type}
Persona: {instruction}

Recent conversation:
{history_text}

Scammer just said: "{message}"

Generate your response (just the message, no explanation):"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        return response.text.strip().strip('"')
    except Exception as e:
        # Fallback responses
        fallback_responses = {
            "phishing": "Why is my account being suspended? What do I need to verify?",
            "lottery": "Really? How do I claim this prize?",
            "job": "What kind of work is it? How much can I earn?",
            "bank": "Is there a problem with my account? What should I do?",
            "other": "Can you tell me more about this?"
        }
        return fallback_responses.get(scam_type, "I'm not sure I understand. Can you explain?")

def extract_intelligence(message: str, all_messages: list) -> dict:
    """Extract intelligence from messages using patterns"""
    
    # Combine all text
    all_text = message + " " + " ".join([m.get('text', '') for m in all_messages])
    
    patterns = {
        "bank_accounts": r'\b\d{9,18}\b',  # 9-18 digit numbers
        "upi_ids": r'\b[\w\.-]+@[\w\.-]+\b',  # user@bank format
        "phone_numbers": r'\b(?:\+91|0)?[6-9]\d{9}\b',  # Indian phone numbers
        "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phishing_links": r'https?://[^\s]+'
    }
    
    intelligence = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, all_text)
        # Deduplicate and filter
        unique = list(set(matches))
        # Filter out obvious false positives
        if key == "bank_accounts":
            unique = [m for m in unique if len(m) >= 10]  # At least 10 digits
        if key == "upi_ids":
            unique = [m for m in unique if '@' in m and '.' not in m.split('@')[0][-4:]]
        
        intelligence[key] = unique[:10]  # Limit to 10 items each
    
    return intelligence

def calculate_threat_level(intel: dict, confidence: float) -> str:
    """Calculate threat level based on intelligence and confidence"""
    
    intel_count = sum(len(v) for v in intel.values())
    
    if confidence >= 0.9 and intel_count >= 3:
        return "critical"
    elif confidence >= 0.7 and intel_count >= 2:
        return "high"
    elif confidence >= 0.5 or intel_count >= 1:
        return "medium"
    else:
        return "low"
    
# ===================== HEALTH =====================

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "AI Honeypot"}

# ===================== GUVI ENDPOINT =====================

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def guvi_honeypot(
    request: IncomingRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    # Validate API key
    if x_api_key != MY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    session_id = request.sessionId
    incoming_msg = request.message.text
    
    # Get or initialize conversation history
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    
    # Add incoming message to history
    conversation_store[session_id].append({
        "sender": request.message.sender,
        "text": incoming_msg,
        "timestamp": request.message.timestamp
    })
    
    # Combine with provided history
    full_history = request.conversationHistory + conversation_store[session_id]
    
    # Count turns
    conversation_turns = len([m for m in full_history if m.get('sender') == 'customer'])
    
    # STEP 1: Detect scam
    scam_detection = detect_scam_with_ai(incoming_msg, full_history)
    is_scam = scam_detection['is_scam']
    confidence = scam_detection['confidence']
    scam_type = scam_detection.get('scam_type', 'other')
    
    # STEP 2: Generate agent response
    if is_scam and confidence >= 0.5:
        engagement_status = "active"
        agent_response = generate_agent_response(incoming_msg, scam_type, full_history, conversation_turns)
        continue_conversation = conversation_turns < 10  # Max 10 turns
    else:
        engagement_status = "monitoring"
        agent_response = "I'm sorry, I don't understand. Can you clarify?"
        continue_conversation = True
    
    # Add agent response to history
    conversation_store[session_id].append({
        "sender": "agent",
        "text": agent_response,
        "timestamp": request.message.timestamp + 1
    })
    
    # STEP 3: Extract intelligence
    all_messages = full_history + [{"text": incoming_msg}]
    extracted_intel = extract_intelligence(incoming_msg, all_messages)
    
    # STEP 4: Calculate threat level
    threat_level = calculate_threat_level(extracted_intel, confidence)
    
    # STEP 5: Build response
    return HoneypotResponse(
        scam_detected=is_scam,
        confidence_score=round(confidence, 2),
        agent_response=agent_response,
        engagement_status=engagement_status,
        conversation_turns=conversation_turns,
        extracted_intelligence=extracted_intel,
        threat_level=threat_level,
        continue_conversation=continue_conversation
    )

# ===================== RUN =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("LOADED API KEY:", os.getenv("API_KEY"))


