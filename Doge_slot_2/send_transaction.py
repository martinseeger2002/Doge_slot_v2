#send_transaction.py
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
    rpc_ip = credentials.get("rpc_ip", "localhost")
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}")

def send_cashout_transaction(input_address, credits):
    credentials = load_rpc_credentials('RPC.conf')
    if not credentials:
        print("Failed to load RPC credentials.")
        return None

    try:
        rpc_connection = get_rpc_connection()
        transaction_id = rpc_connection.sendtoaddress(input_address, credits)
        print(f"Transaction successful. Transaction ID: {transaction_id}")
        return transaction_id
    except Exception as e:
        print(f"Error while sending transaction: {e}")
        return None
