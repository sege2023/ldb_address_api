import re

def is_valid_base58(address):
    """Check if address is valid Base58 format"""
    # using regex for Base58 characters would use base58 lib in production
    base58_pattern = r'^[0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$'
    
    if not re.match(base58_pattern, address):
        return False
    
    if len(address) < 20:  
        return False
    
    return True


def is_valid_ethereum(address):
    """Validate Ethereum address format"""
    pattern = r'^0x[a-fA-F0-9]{40}$'
    result = bool(re.match(pattern, address))
    return result

def guess_network(address):
    """Guess network from address prefix"""
    if address.startswith("0x"):
        return "Ethereum"
    elif address.startswith("LDB"):
        return "LDB"
    elif address.startswith("bc1") or address.startswith("1") or address.startswith("3"):
        return "Bitcoin"
    elif address.startswith("T") or address.startswith("t"):
        return "Tron"
    else:
        return "Unknown"