from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def check_dogecoin():
    rpc_username = 'your_rpc_user'
    rpc_password = 'your_rpc_password'
    rpc_ip = '192.168.68.57'  # Dogecoin Core IP address

    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_username}:{rpc_password}@{rpc_ip}:22555')
        print("Connection successful")
        info = rpc_connection.getinfo()
        print("Retrieved Dogecoin Core information")
        if 'version' in info:
            return f"Dogecoin Core version: {info['version']} (running)"
        else:
            print("Version information not available")
    except (ConnectionRefusedError, JSONRPCException) as e:
        print(f"Connection error: {e}")

    return "Dogecoin Core is not running"

if __name__ == "__main__":
    dogecoin_status = check_dogecoin()
    print(dogecoin_status)
