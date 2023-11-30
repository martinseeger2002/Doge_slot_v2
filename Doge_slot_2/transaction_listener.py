# transaction_listener.py

from bitcoinrpc.authproxy import AuthServiceProxy
import time

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

def check_incoming_transactions(slot_address):
    print('Hey now! Checking for incoming transactions...')
    credentials = load_rpc_credentials('RPC.conf')
    if not credentials:
        print("Failed to load RPC credentials.")
        return None, None, None  # Return None for each value if credentials are missing

    rpc_connection = get_rpc_connection(credentials)
    most_recent_tx = None
    most_recent_tx_time = 0

    try:
        # Get recent transactions
        transactions = rpc_connection.listtransactions("*", 100)
        for tx in transactions:
            # Check if the transaction is relevant and more recent
            if tx['category'] == 'receive' and tx['address'] == slot_address:
                tx_time = tx.get('time', 0)
                if tx_time > most_recent_tx_time:
                    most_recent_tx_time = tx_time
                    most_recent_tx = tx
    except Exception as e:
        print(f"Error in checking transactions: {e}")
        return None, None, None  # Return None for each value in case of an exception

    if most_recent_tx:
        amount = most_recent_tx['amount']
        txid = most_recent_tx['txid']
        new_input_address = None

        try:
            # Get the complete transaction details
            raw_tx = rpc_connection.getrawtransaction(txid, True)
            for vin in raw_tx['vin']:
                # Get previous transaction ID
                prev_txid = vin['txid']
                prev_raw_tx = rpc_connection.getrawtransaction(prev_txid, True)
                
                # Get the address from the previous transaction's outputs
                prev_vout = prev_raw_tx['vout'][vin['vout']]
                if 'addresses' in prev_vout['scriptPubKey']:
                    new_input_address = prev_vout['scriptPubKey']['addresses'][0]  # Assuming first address is the relevant one
                    break  # Exit loop after finding the first address
        except Exception as e:
            print(f"Error in processing transaction details: {e}")

        return amount, new_input_address, txid  # Return the amount, input address, and txid

    return None, None, None  # Return None for each value if no recent transaction is found
