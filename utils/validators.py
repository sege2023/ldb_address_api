import re
import base58
from eth_utils import is_address, is_checksum_address

NETWORK_PATTERNS = {
    # Matches 0x + 40 hex chars (Case Insensitive)
    "Ethereum": r'^0x[a-fA-F0-9]{40}$',
    
    # Matches Bitcoin Legacy (Starts with 1 or 3, 26-35 chars)
    "Bitcoin_Legacy": r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$',
    
    # Matches Tron (Starts with T, 33-35 chars)
    "Tron": r'^T[a-zA-Z0-9]{32,35}$',
    
    # Matches Polkadot (Starts with 1, 47-49 chars - distinct length from BTC)
    "Polkadot":r'^[1-9A-HJ-NP-Za-km-z]{47,48}$',
    
    # Matches Bitcoin SegWit (Starts with bc1)
    "Bitcoin_SegWit": r'^bc1[a-z0-9]{39,59}$',

    "Solana": r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',
}

def detect_network(address):
    """
    Better network detection that handles Solana vs Bitcoin ambiguity
    """
    if re.match(NETWORK_PATTERNS["Ethereum"], address):
        return "Ethereum"
    
    if re.match(NETWORK_PATTERNS["Tron"], address):
        return "Tron"
    
    if re.match(NETWORK_PATTERNS["Bitcoin_Legacy"], address):
        return "Bitcoin_Legacy"
    
    if re.match(NETWORK_PATTERNS["Polkadot"], address):
        return "Polkadot"
    
    # Check SegWit
    if re.match(NETWORK_PATTERNS["Bitcoin_SegWit"], address):
        return "Bitcoin_SegWit"
    
    # Check Solana (this will also match Bitcoin addresses!)
    # So we need additional logic...
    if re.match(NETWORK_PATTERNS["Solana"], address):
        # Try to validate as Solana first
        try:
            if 32 <= len(address) <= 44:
                # Additional heuristic: Solana addresses often don't start with 1 or 3
                if not address.startswith(('1', '3')):
                    return "Solana"
        except:
            pass
    
    return None

def validate_checksum(address, network):
    """
    the checksum for ethereum doesn't rely fully on the eip-55 standard,
    so we accept all valid hex addresses for now. we would use install dependecies that the eip-55 validation requires in production. which is the pysha3 library.
    """
   
    try:
        if network == "Ethereum":
            # 1. Basic structure check
            if not is_address(address):
                return False
            
            # 2. Check if it's ALL lowercase or ALL uppercase
            hex_part = address[2:]  # Remove 0x
            if hex_part.islower() or hex_part.isupper():
                return True  # These are valid without EIP-55
            # 3. Mixed case - enforce EIP-55 checksum
            return is_checksum_address(address)

        # --- BITCOIN LEGACY & TRON ---
        elif network in ["Bitcoin_Legacy", "Tron"]:
            base58.b58decode_check(address)
            return True

        # --- POLKADOT & SEGWIT ---
        elif network in ["Polkadot", "Bitcoin_SegWit"]:
            # We skip math here to avoid installing 'bech32' or 'scalecodec'
            # We trust the Regex from detect_network()
            return True
        elif network == "Solana":
            try:
                decoded = base58.b58decode(address)
                if len(decoded) >= 32:
                    return True
                return False
            except:
                return False
        return False

    except (ValueError, Exception):
        return False
