from fastapi import FastAPI, Header, HTTPException,Request
from pydantic import BaseModel, Field
from typing import List, Dict
import os
import re
import json

app = FastAPI(title="Honeypot Scam Detector")

MY_API_KEY = os.getenv("API_KEY")

# ===================== MODELS =====================

class Message(BaseModel):
    role: str
    message: str

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int | float   # ✅ FIX 1

class IncomingRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: list = Field(default_factory=list)  # ✅ FIX 2
    metadata: dict = Field(default_factory=dict)             # ✅ FIX 2

class HoneypotResponse(BaseModel):
    scam_detected: bool
    confidence_score: float
    agent_response: str
    engagement_status: str
    conversation_turns: int
    extracted_intelligence: Dict[str, List[str]]
    threat_level: str
    continue_conversation: bool

# ===================== DUMMY SAFE FUNCTIONS (LOCAL TEST) =====================

def detect_scam(message: str) -> dict:
    return {
        "is_scam": True,
        "confidence": 0.9,
        "scam_type": "account_verification"
    }

def generate_persona_response(message: str, scam_type: str, history: list) -> str:
    return "Why is my account being suspended?"

def extract_intelligence(message: str):
    return {
        "bank_accounts": [],
        "upi_ids": [],
        "phishing_links": [],
        "phone_numbers": [],
        "emails": []
    }

def calculate_threat_level(intel):
    return "low"

# ===================== HEALTH =====================

@app.get("/")
async def health_check():
    return {"status": "healthy"}

# ===================== GUVI ENDPOINT =====================

@app.post("/api/honeypot")
async def guvi_honeypot(
    request: IncomingRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if x_api_key != MY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    reply = "Why is my account being suspended?"

    return {
        "status": "success",
        "reply": reply
    }

# ===================== RUN =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
