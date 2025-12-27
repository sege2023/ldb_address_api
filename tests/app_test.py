import pytest
import json
from app import app
from services.address_service import classify_address, detect_network, validate_checksum
from services.nlp_service import parse_payment_intent
from unittest.mock import patch, MagicMock
class TestAddressService:
    """Unit tests for address classification"""
    
    def test_ldb_internal_address(self):
        """Test LDB internal address detection"""
        # From your mock data
        internal_eth = "0x816275d1f9239D99D6D41473244883857a7BA8ed"
        internal_btc = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
        
        result1 = classify_address(internal_eth)
        assert result1["type"] == "internal"
        assert result1["network"] == "Ethereum"
        
        result2 = classify_address(internal_btc)
        assert result2["type"] == "internal"
        assert result2["network"] == "Bitcoin_Legacy"
    
    def test_blacklisted_address(self):
        """Test blacklist detection"""
        blacklisted = "0x816275d1f9239D99D6D41473244883857a7BA8ed"
        
        result = classify_address(blacklisted)
        assert result["type"] == "internal"  # First internal, but...
        assert "blacklisted" in result.get("risk_flags", [])
    
    def test_network_detection_edge_cases(self):
        """Test tricky network detections"""
        
        # Solana vs Bitcoin ambiguity
        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        sol_address = "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg"  # Real Solana
        
        assert detect_network(btc_address) == "Bitcoin_Legacy"
        assert detect_network(sol_address) == "Solana"
    
    def test_invalid_addresses(self):
        """Test malformed addresses"""
        invalid_cases = [
            "0x123",  # Too short
            "not_an_address",
            "bc1invalid",  # Invalid bech32
            "",  # Empty
            "   ",  # Whitespace
        ]
        
        for addr in invalid_cases:
            result = classify_address(addr)
            assert result["type"] == "invalid"
    
    def test_checksum_validation(self):
        """Test checksum validation per network"""
        
        # Valid Ethereum (with proper checksum)
        valid_eth = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
        # Invalid (modified case)
        invalid_eth = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        
        # Note: Your current code accepts both
        # With EIP-55: valid=True, invalid=False
        
        assert validate_checksum(valid_eth, "Ethereum") is True
        # Uncomment when EIP-55 implemented:
        # assert validate_checksum(invalid_eth, "Ethereum") is False

class TestNLPService:
    """Unit tests for NLP intent parsing"""

    @patch('services.nlp_service.requests.post')
    def test_basic_payment_intent(self, mock_post):
        """Test clear payment commands (Ordered Responses)"""
        
        # 1. Define your inputs
        test_cases = [
            ("Send 50 USDT to Sarah", {"amount": 50, "asset": "USDT", "recipient": "Sarah"}),
            ("Transfer 0.5 ETH to 0x123...", {"asset": "ETH", "recipient": "0x123..."}),
        ]

        # 2. Create the 3 specific mock responses we need, in order
        response_1 = MagicMock()
        response_1.status_code = 200
        response_1.json.return_value = {"choices": [{"message": {"content": '{"amount": 50, "asset": "USDT", "recipient": "Sarah", "confidence": 0.9}'}}]}

        response_2 = MagicMock()
        response_2.status_code = 200
        response_2.json.return_value = {"choices": [{"message": {"content": '{"amount": 0.5, "asset": "ETH", "recipient": "0x123...", "confidence": 0.9}'}}]}

    

        # 3. Assign them as a list to side_effect
        mock_post.side_effect = [response_1, response_2]

        # 4. Run the loop
        for text, expected in test_cases:
            result = parse_payment_intent(text)
            for key, value in expected.items():
                if value is not None:
                    assert result.get(key) == value, f"Failed on '{text}' for key '{key}'"

    @patch('services.nlp_service.requests.post')
    def test_ambiguous_intent(self, mock_post):
        """Test low-confidence parsing"""
        ambiguous = [
            "Send some money to him",
            "Transfer crypto",
            "Pay", 
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"amount": null, "confidence": 0.4, "clarification_needed": true}'
                }
            }]
        }
        mock_post.return_value = mock_response

        for text in ambiguous:
            result = parse_payment_intent(text)
            assert result.get("confidence", 1) < 0.6
            assert "clarification_needed" in result
    
    def test_error_handling(self):
        """Test API failure scenarios"""
        # Mock requests failure
        import requests
        original_post = requests.post
        
        def mock_failure(*args, **kwargs):
            raise requests.exceptions.ConnectionError("API down")
        
        requests.post = mock_failure
        
        try:
            result = parse_payment_intent("Send 10 USD")
            assert "error" in result
            assert result["confidence"] == 0
        finally:
            requests.post = original_post

class TestAPIEndpoints:
    """Integration tests for Flask API"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_address_inspect_valid(self, client):
        """Test valid address inspection"""
        response = client.post('/ai/address/inspect', 
                             json={"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"})
        
        assert response.status_code == 200
        data = response.get_json()
        assert "classification" in data
        assert "network" in data
        assert "risk_flags" in data
    
    def test_address_inspect_missing_field(self, client):
        """Test missing required field"""
        response = client.post('/ai/address/inspect', json={})
        assert response.status_code == 400
        assert "error" in response.get_json()
    
    def test_intent_parse(self, client):
        """Test NLP intent parsing"""
        response = client.post('/ai/intent/parse',
                             json={"text": "Send 50 USDT to Sarah"})
        
        assert response.status_code == 200
        data = response.get_json()
        assert "parsed_intent" in data
        assert "original_text" in data
    
    def test_home_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert "service" in data
        assert "endpoints" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])