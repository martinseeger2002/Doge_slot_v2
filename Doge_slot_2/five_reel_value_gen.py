import random
from bitcoinrpc.authproxy import AuthServiceProxy


def load_rpc_credentials(filename):
    """Load RPC credentials from a configuration file."""
    credentials = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('=')
            if len(parts) == 2:
                credentials[parts[0]] = parts[1]
    return credentials

def get_rpc_connection():
    """Establish RPC connection using credentials."""
    credentials = load_rpc_credentials('RPC.conf')
    rpc_user = credentials.get("rpc_user", "default_user")
    rpc_password = credentials.get("rpc_password", "default_password")
    rpc_port = credentials.get("rpc_port", "22555")
    rpc_ip = credentials.get("rpc_ip", "localost")
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}")

def get_random_tx_data():
    """Get random hex characters from a block's transaction data."""
    rpc_connection = get_rpc_connection()
    block_count = rpc_connection.getblockcount()
    random_block_number = random.randint(max(0, block_count - 1000), block_count)
    block_hash = rpc_connection.getblockhash(random_block_number)
    block = rpc_connection.getblock(block_hash)
    
    tx_data = ""
    if block["tx"]:
        tx_data = ''.join(block["tx"])
    
    return tx_data

def load_icon_mappings(filename):
    """Load slot icon mappings from a configuration file."""
    mapping = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('=')
            if len(parts) == 2:
                mapping[parts[0]] = parts[1]
    return mapping

def generate_reel_result(mapping, hex_segment):
    """Generate reel result for a specific hex segment."""
    return mapping.get(hex_segment, "default_icon.png")

def spin_reels():
    """Main function to spin reels and generate slot results."""
    reel_results = []
    tx_data = get_random_tx_data()

    if len(tx_data) < 10:
        return ["error"] * 5

    hex_segments = [tx_data[i:i+2] for i in random.sample(range(len(tx_data) - 2), 5)]

    for i in range(1, 6):
        icon_mappings = load_icon_mappings(f"reel{i}_icon_mapping.conf")
        reel_result = generate_reel_result(icon_mappings, hex_segments[i-1])
        reel_results.append(reel_result)

    return reel_results

# Example use of spin_reels function
results = spin_reels()
print(results)
