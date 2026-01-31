from fastapi import FastAPI, Header, HTTPException,Request
from pydantic import BaseModel
from typing import List, Dict
import os
import re
from google import genai
from google.genai import types
import json

# ============================================
# SETUP
# ============================================
app = FastAPI(title="Honeypot Scam Detector")

# Your API Key (for authentication)
MY_API_KEY = os.getenv("API_KEY")

# Configure Gemini with new API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================
# DATA MODELS
# ============================================
class Message(BaseModel):
    role: str
    message: str

class IncomingRequest(BaseModel):
    conversation_id: str
    message: str
    conversation_history: List[Message] = []

class HoneypotResponse(BaseModel):
    scam_detected: bool
    confidence_score: float
    agent_response: str
    engagement_status: str
    conversation_turns: int
    extracted_intelligence: Dict[str, List[str]]
    threat_level: str
    continue_conversation: bool

# ============================================
# FUNCTION 1: SCAM DETECTION
# ============================================
def detect_scam(message: str) -> dict:
    """Uses Gemini AI to detect if message is a scam"""
    
    prompt = f"""You are a scam detection expert. Analyze this message and determine if it's a scam.

Message: "{message}"

Look for these scam indicators:
- Prize/lottery fraud
- Urgent account verification requests
- Too-good-to-be-true offers
- Requests for money or personal information
- Phishing attempts
- Work-from-home scams

Return ONLY a JSON object (no markdown, no extra text, no code blocks):
{{
  "is_scam": true or false,
  "confidence": 0.0 to 1.0,
  "scam_type": "lottery_fraud" or "phishing" or "account_verification" or "job_scam" or "none",
  "reasoning": "brief explanation"
}}"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=200
            )
        )
        
        result = response.text.strip()
        
        # Remove markdown code blocks if present
        result = result.replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON response
        return json.loads(result)
    except Exception as e:
        print(f"Error in scam detection: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
        return {
            "is_scam": False,
            "confidence": 0.5,
            "scam_type": "unknown",
            "reasoning": "Error in detection"
        }

# ============================================
# FUNCTION 2: GENERATE PERSONA RESPONSE
# ============================================
def generate_persona_response(message: str, scam_type: str, history: List[Message]) -> str:
    """Generate a believable victim response to keep scammer engaged"""
    
    # Build conversation context
    history_text = "\n".join([f"{msg.role}: {msg.message}" for msg in history[-5:]])
    
    prompt = f"""You are roleplaying as a 65-year-old person named Ramesh who is not tech-savvy and trusting.

SCAM TYPE: {scam_type}
SCAMMER'S LATEST MESSAGE: "{message}"

PREVIOUS CONVERSATION:
{history_text}

YOUR GOAL (secret - don't reveal):
- Extract bank account numbers
- Extract UPI IDs  
- Extract phishing links
- Extract phone numbers
- Keep them talking

YOUR CHARACTER:
- Elderly, not good with technology
- Eager and excited about offers
- Asks clarifying questions
- Shows interest but needs help with "technical" steps
- Confused about online payments

RULES:
- Keep response SHORT (1-2 sentences max)
- Sound natural and human
- Never reveal you know it's a scam
- Ask questions that lead them to share details
- Show eagerness to comply
- Use simple language, occasional typos are okay

Generate ONLY the response message (no explanations, no quotes, no preamble):"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=100
            )
        )
        
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm interested! Please tell me more about this."

# ============================================
# FUNCTION 3: EXTRACT INTELLIGENCE
# ============================================
def extract_intelligence(message: str) -> Dict[str, List[str]]:
    """Extract sensitive information from scammer's message"""
    
    intelligence = {
        "bank_accounts": [],
        "upi_ids": [],
        "phishing_links": [],
        "phone_numbers": [],
        "emails": []
    }
    
    # Bank Account Numbers (9-18 digits)
    bank_pattern = r'\b\d{9,18}\b'
    intelligence["bank_accounts"] = list(set(re.findall(bank_pattern, message)))
    
    # UPI IDs (format: text@bank or phone@bank)
    upi_pattern = r'\b[\w\.\-]+@[a-zA-Z]+\b'
    potential_upis = re.findall(upi_pattern, message)
    # Filter for common UPI handles
    intelligence["upi_ids"] = [upi for upi in potential_upis if any(bank in upi.lower() for bank in 
        ['paytm', 'phonepe', 'gpay', 'upi', 'ybl', 'okicici', 'oksbi', 'okhdfcbank', 'okaxis'])]
    
    # URLs/Phishing Links
    url_pattern = r'https?://[^\s]+'
    intelligence["phishing_links"] = list(set(re.findall(url_pattern, message)))
    
    # Phone Numbers (Indian: 10 digits or +91 followed by 10 digits)
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}'
    intelligence["phone_numbers"] = list(set(re.findall(phone_pattern, message)))
    
    # Email Addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    all_emails = re.findall(email_pattern, message)
    # Exclude UPIs from emails
    intelligence["emails"] = [email for email in all_emails if email not in intelligence["upi_ids"]]
    
    return intelligence

# ============================================
# FUNCTION 4: CALCULATE THREAT LEVEL
# ============================================
def calculate_threat_level(intel: Dict[str, List[str]]) -> str:
    """Calculate threat level based on extracted intelligence"""
    
    score = (
        len(intel["bank_accounts"]) * 3 +
        len(intel["upi_ids"]) * 3 +
        len(intel["phishing_links"]) * 2 +
        len(intel["phone_numbers"]) * 1 +
        len(intel["emails"]) * 1
    )
    
    if score >= 6:
        return "critical"
    elif score >= 3:
        return "high"
    elif score >= 1:
        return "medium"
    else:
        return "low"

# ============================================
# MAIN API ENDPOINT
# ============================================
@app.post("/detect-and-engage", response_model=HoneypotResponse)
async def detect_and_engage(
    request: IncomingRequest,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Main honeypot endpoint that:
    1. Authenticates the request
    2. Detects scam intent
    3. Generates persona response
    4. Extracts intelligence
    5. Returns structured response
    """
    
    # ========================================
    # STEP 1: AUTHENTICATE (Check API Key)
    # ========================================
    if x_api_key != MY_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key"
        )
    
    # ========================================
    # STEP 2: DETECT SCAM
    # ========================================
    detection_result = detect_scam(request.message)
    
    # ========================================
    # STEP 3: GENERATE RESPONSE (if scam detected)
    # ========================================
    agent_response = ""
    if detection_result["is_scam"]:
        agent_response = generate_persona_response(
            request.message,
            detection_result["scam_type"],
            request.conversation_history
        )
    else:
        agent_response = "I'm sorry, I don't understand. Could you explain more?"
    
    # ========================================
    # STEP 4: EXTRACT INTELLIGENCE
    # ========================================
    extracted_intel = extract_intelligence(request.message)
    
    # ========================================
    # STEP 5: DETERMINE IF CONVERSATION CONTINUES
    # ========================================
    current_turn = len(request.conversation_history) // 2 + 1
    
    # Continue if:
    # - It's a scam AND
    # - We haven't reached max turns (10) AND
    # - We don't have enough intel yet
    has_valuable_intel = (
        len(extracted_intel["bank_accounts"]) > 0 or
        len(extracted_intel["upi_ids"]) > 0 or
        len(extracted_intel["phishing_links"]) > 0
    )
    
    should_continue = (
        detection_result["is_scam"] and
        current_turn < 10 and
        not has_valuable_intel
    )
    
    # ========================================
    # STEP 6: BUILD RESPONSE
    # ========================================
    return HoneypotResponse(
        scam_detected=detection_result["is_scam"],
        confidence_score=detection_result["confidence"],
        agent_response=agent_response,
        engagement_status="active" if should_continue else "completed",
        conversation_turns=current_turn,
        extracted_intelligence=extracted_intel,
        threat_level=calculate_threat_level(extracted_intel),
        continue_conversation=should_continue
    )

# ============================================
# HEALTH CHECK ENDPOINT (for testing)
# ============================================
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "Honeypot Scam Detector",
        "version": "1.0"
    }
@app.get("/api/honeypot", include_in_schema=False)
async def guvi_honeypot_check(request: Request):
    api_key = request.headers.get("x-api-key")

    if api_key != MY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {
        "status": "ok",
        "honeypot": "active",
        "service": "agentic-honeypot",
        "message": "Honeypot endpoint reachable and authenticated"
    }

# ============================================
# RUN THE APP
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)