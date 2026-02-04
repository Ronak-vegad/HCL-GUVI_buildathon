# AI-Powered Agentic Honey-Pot System

**Hackathon:** HCL-GUVI Buildathon 2026  
**Team:** Ronak Vegad

## Overview

This is an AI-powered honeypot system that detects scam messages and autonomously engages scammers through multi-turn conversations to extract actionable intelligence.

## Features

✅ **Scam Detection** - Uses Gemini AI to identify phishing, lottery, job scams, and fake banking alerts  
✅ **Autonomous Agent** - Generates believable, persona-based responses to keep scammers engaged  
✅ **Intelligence Extraction** - Extracts bank accounts, UPI IDs, phone numbers, emails, and phishing links  
✅ **Threat Assessment** - Calculates threat levels based on confidence and extracted intelligence  
✅ **Multi-turn Conversations** - Maintains conversation state across multiple interactions  

## API Endpoint

**POST** `/api/honeypot`

**Headers:**
```
x-api-key: alterEgOI2345hCiGUvi_Buildathon
Content-Type: application/json
```

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "customer",
    "text": "Your message text",
    "timestamp": 1769776585000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "RMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "scam_detected": true,
  "confidence_score": 0.8,
  "agent_response": "Why is my account being suspended?",
  "engagement_status": "active",
  "conversation_turns": 1,
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": [],
    "phone_numbers": [],
    "emails": [],
    "phishing_links": []
  },
  "threat_level": "medium",
  "continue_conversation": true
}
```

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables** (`.env`):
   ```
   GEMINI_API_KEY=your_gemini_api_key
   API_KEY=alterEgOI2345hCiGUvi_Buildathon
   ```

3. **Run the server:**
   ```bash
   uv run python main.py
   ```

4. **Test locally:**
   ```bash
   python test_api.py
   ```

## Technologies

- **FastAPI** - High-performance web framework
- **Gemini 2.0 Flash** - AI for scam detection and response generation
- **Pydantic** - Data validation and modeling
- **Regex** - Pattern matching for intelligence extraction

## How It Works

1. **Incoming message** is analyzed by Gemini AI for scam patterns
2. **If scam detected** (confidence ≥ 0.5), autonomous agent activates
3. **Agent generates** persona-based response to engage scammer
4. **Intelligence extraction** runs on message and conversation history
5. **Threat level** is calculated based on confidence and extracted data
6. **Response returned** with all evaluation metrics

## Deployment

Deploy to Render, Heroku, or any platform supporting Python web apps:
- Ensure `GEMINI_API_KEY` and `API_KEY` are set in environment
- Use `uv run python main.py` or configure with `uvicorn main:app --host 0.0.0.0 --port $PORT`

## License

MIT License - Built for HCL-GUVI Buildathon 2026
