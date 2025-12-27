import json
from utils.validators import detect_network, validate_checksum
from config import DATA_PATH
import re
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
    data = load_mock_data()
    
    # --- Step 1: Regex & Checksum Validation ---
    detected_network = detect_network(address)
    
    if not detected_network:
        return {
            "type": "invalid",
            "reason": "Unknown Format", 
            "network": None,
            "risk_flags": []
        }

    is_valid = validate_checksum(address, detected_network)
    
    # ERROR HANDLE: If validation failed, return NOW.
    if not is_valid:
        return {
            "type": "invalid",
            "reason": "Invalid Checksum", 
            "network": detected_network,
            "risk_flags": []
        }

    risk_flags = []
    
    # 2. Check Blacklist FIRST (or independently)
    if address in data["blacklist"]:
        risk_flags.append("blacklisted")
    
    # Step 2: Check if internal
    if address in data["internal_addresses"]:
        return {
            "type": "internal",
            "reason": "found_in_internal_db",
            "network": detected_network,
            "risk_flags": risk_flags
        }
    
    # Step 3: Check blacklist
    risk_flags = []
    if address in data["blacklist"]:
        risk_flags.append("blacklisted")
    
    # Step 4: Final Return for Valid External Address
    return {
        "type": "external_valid",
        "reason": "valid_external_address",
        "network": detected_network, # Use the network we already detected
        "risk_flags": risk_flags
    }