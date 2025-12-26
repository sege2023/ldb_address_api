import requests
import json
from config import OPENROUTER_KEY, OPENROUTER_MODEL

"""
NLP Intent Parser

Production Contact Resolution:
-------------------------------
SELECT c.contact_address 
FROM user_contacts c
WHERE c.user_id = %s          -- From auth token
AND LOWER(c.contact_name) = %s -- Case-insensitive
AND c.is_active = TRUE;

Note: This service only parses intent.
Backend must resolve recipient using authenticated user's context.
"""

def parse_payment_intent(text):
    """
    Use OpenRouter to extract payment intent from natural language
    Returns: {amount, asset, recipient, confidence}
    """
    prompt = f"""Extract payment intent from this text: "{text}"

    Return ONLY valid JSON with this exact structure:
    {{
    "amount": <number or null>,
    "asset": "<token symbol or null>",
    "recipient": "<name/address or null>",
    "confidence": <0-1>
    }}

    Examples:
    "Send 50 USDT to Sarah" → {{"amount": 50, "asset": "USDT", "recipient": "Sarah", "confidence": 0.95}}
    "Transfer half my ETH to Bob" → {{"amount": null, "asset": "ETH", "recipient": "Bob", "confidence": 0.7}}
    """

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract content
        content = result['choices'][0]['message']['content']
        
        content = content.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        parsed = json.loads(content)
        
        # Add clarification if confidence is low
        if parsed.get('confidence', 0) < 0.6:
            parsed['clarification_needed'] = "Ambiguous request. Please specify amount and recipient clearly."
        
        return parsed
        
    except requests.exceptions.RequestException as e:
        return {
            "error": "API request failed",
            "details": str(e),
            "amount": None,
            "asset": None,
            "recipient": None,
            "confidence": 0
        }
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse AI response",
            "details": str(e),
            "amount": None,
            "asset": None,
            "recipient": None,
            "confidence": 0
        }