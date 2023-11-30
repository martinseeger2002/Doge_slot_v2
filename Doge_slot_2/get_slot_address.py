from bitcoinrpc.authproxy import AuthServiceProxy

# Global slot address variable
slot_address = None

def load_rpc_credentials(filename):
    """
    Load RPC credentials from a configuration file.
    The file should contain lines in the format 'key=value'.
    """
    credentials = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                key, _, value = line.strip().partition('=')
                if key and value:
                    credentials[key] = value
        return credentials
    except IOError as e:
        print(f"Error reading file {filename}: {e}")
        return {}

def get_rpc_connection(credentials):
    """
    Establish an RPC connection using credentials.
    """
    rpc_user = credentials.get("rpc_user", "default_user")
    rpc_password = credentials.get("rpc_password", "default_password")
    rpc_port = credentials.get("rpc_port", "22555")
    rpc_ip = credentials.get("rpc_ip", "localhost")  # Corrected typo 'localost'
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}")

def get_new_address():
    """
    Generate a new Bitcoin address using RPC.
    """
    credentials = load_rpc_credentials('RPC.conf')
    if not credentials:
        print("Failed to load RPC credentials.")
        return None

    rpc_connection = get_rpc_connection(credentials)
    try:
        return rpc_connection.getnewaddress()
    except Exception as e:
        print(f"Error getting new address: {e}")
        return None

def check_and_update_slot_address():
    """
    Update the global slot address with a new Bitcoin address.
    """
    global slot_address
    slot_address = get_new_address()
    if slot_address:
        print(f"New slot address generated: {slot_address}")
    else:
        print("Failed to generate a new slot address.")
    return slot_address

