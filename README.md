# LDB Address Classifier + NLP Parser

## Quick Start
```bash
pip install -r requirements.txt
export OPENROUTER_KEY="your-key-here"
python app.py
```

## Endpoints

### 1. Address Inspector
```bash
curl -X POST http://localhost:5000/ai/address/inspect \
  -H "Content-Type: application/json" \
  -d '{"address": "LDB1a2b3c4d5e6f7g8h9"}'
```

### 2. Intent Parser
```bash
curl -X POST http://localhost:5000/ai/intent/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Send 50 USDT to Sarah"}'
```

## What's Included
✅ Base58 address validation  
✅ Internal/external classification  
✅ Risk flag detection  
✅ Natural language parsing  

## What's NOT Included (Needs Contract)
❌ Real database integration  
❌ Production error handling  
❌ Comprehensive testing  
❌ Deployment configuration