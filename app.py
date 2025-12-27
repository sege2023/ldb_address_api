from flask import Flask, request, jsonify
from datetime import datetime
from services.address_service import classify_address
from services.nlp_service import parse_payment_intent

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "service": "LDB Address Classifier + NLP Parser",
        "version": "0.1.0 (prototype)",
        "endpoints": [
            "POST /ai/address/inspect",
            "POST /ai/intent/parse"
        ]
    }

@app.route('/ai/address/inspect', methods=['POST'])
def inspect_address():
    """
    Classify and validate crypto address
    
    Body: {"address": "LDB1a2b3c4..."}
    """
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({"error": "Missing 'address' field"}), 400
    
    address = data['address']
    classification = classify_address(address)
    
    return jsonify({
        "address": address,
        "classification": classification['type'],
        "reason": classification['reason'],
        "network": classification['network'],
        "risk_flags": classification['risk_flags'],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/ai/intent/parse', methods=['POST'])
def parse_intent():
    """
    Parse natural language payment command
    
    Body: {"text": "Send 50 USDT to Sarah"}
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    
    text = data['text']
    intent = parse_payment_intent(text)
    
    return jsonify({
        "original_text": text,
        "parsed_intent": intent,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    addresses = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", # Valid BTC
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb", # Invalid BTC (Typo at end)
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", # Valid ETH
        "TNDFkDS9vD34M479h61j91a5fF7833f99"    # Valid Tron
    ]
    
    print(f"{'ADDRESS':<45} | {'NETWORK':<10} | {'VALID'}")
    print("-" * 70)
    for addr in addresses:
        res = classify_address(addr)
        print(f"{addr:<45} | {str(res['network']):<10} | {res['valid']}")
