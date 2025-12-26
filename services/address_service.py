import json
from utils.validators import is_valid_base58, guess_network, is_valid_ethereum
from config import DATA_PATH
"""
Address Classification Service

Production SQL for internal address lookup:
-------------------------------------------
SELECT w.id, w.address, w.user_id, w.blockchain_network
FROM wallets w
WHERE w.address = %s AND w.is_active = TRUE;

If row exists → internal (managed by LDB)
If no row → external (third-party wallet)

Risk flags would join against:
- blacklist table (known scam addresses)
- compliance_flags table (AML/KYC issues)
- frozen_wallets table (admin-locked accounts)
"""
def load_mock_data():
    """Load mock addresses from JSON"""
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def classify_address(address):
    """
    Classify address as:
    - internal: LDB internal address
    - external_valid: Valid external address
    - invalid: Malformed address
    """
    data = load_mock_data()
    
    if address.startswith("0x"):
        if not is_valid_ethereum(address):
            return {
                "type": "invalid",
                "reason": "malformed_address",
                "network": None,
                "risk_flags": []
            }
    else:
        # Check Base58 for non-ETH addresses
        if not is_valid_base58(address):
            return {
                "type": "invalid",
                "reason": "malformed_address",
                "network": None,
                "risk_flags": []
            }
    #
    
    # Step 2: Check if internal
    # this is a mock check against loaded data we would query a real DB in production on an indexed column
    if address in data["internal_addresses"]:
        return {
            "type": "internal",
            "reason": "found_in_internal_db",
            "network": "LDB",
            "risk_flags": []
        }
    
    # Step 3: Check blacklist
    risk_flags = []
    if address in data["blacklist"]:
        risk_flags.append("blacklisted")
    
    # Step 4: Guess network
    network = guess_network(address)
    
    return {
        "type": "external_valid",
        "reason": "valid_external_address",
        "network": network,
        "risk_flags": risk_flags
    }