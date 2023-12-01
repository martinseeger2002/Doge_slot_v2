from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from http.server import HTTPServer, SimpleHTTPRequestHandler
from flask import Flask, jsonify
from flask_cors import CORS
import five_reel_value_gen
from flask import session
import time
import threading
import requests
import json
import os
import QR_gen

os.chdir('C:\\Doge_slot_1\\doge_slot_1\\python')

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        return super().end_headers()



app = Flask(__name__)
CORS(app)


# Global File Paths
IMAGE_DIR = "C:/Doge_slot_1/doge_slot_1/images/"
CONFIG_DIR = "C:/Doge_slot_1/doge_slot_1/python/"


# Replace these with your actual RPC credentials and port
rpc_user = "your_rpc_user"
rpc_password = "your_rpc_password"
rpc_port = "22555"
rpc_host = "localhost"


# Function to create an RPC connection and send a request
def send_rpc_request(method, params=[]):
    url = f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}"
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()


# Global variables
isOperationInProgress = False
bet_amount = 0  # Initial default value
creditsTotal = 20
processed_tx_ids = set()
win = 0
results = ['reel_icon_1.png', 'reel_icon_2.png', 'reel_icon_3.png', 'reel_icon_4.png', 'reel_icon_5.png']
input_address = "none"
generated_address = None



# Function to get senders address
def get_input_address_of_latest_received_transaction(rpc_user, rpc_password, rpc_host, rpc_port):
    global input_address, generated_address
    try:
        # Connect to the Bitcoin node
        rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")

        # List recent transactions for the wallet
        transactions = rpc_connection.listtransactions("*", 10, 0, True)  # Check the last 10 transactions

        for transaction in transactions:
            # Check if the transaction is a receiving transaction to the generated address
            if transaction['category'] == 'receive' and transaction['address'] == generated_address:
                # Get the transaction details
                transaction_details = rpc_connection.getrawtransaction(transaction['txid'], True)

                # Assuming it's a standard transaction with inputs
                input_txid = transaction_details['vin'][0]['txid']
                input_vout = transaction_details['vin'][0]['vout']
                input_transaction = rpc_connection.getrawtransaction(input_txid, True)
                input_address = input_transaction['vout'][input_vout]['scriptPubKey']['addresses'][0]

                return input_address

        print("No receiving transactions found to the generated address.")
        return None

    except JSONRPCException as e:
        print(f"An error occurred: {e}")
        return None


address = get_input_address_of_latest_received_transaction(rpc_user, rpc_password, rpc_host, rpc_port)
if address is None:
    print("No address found in the latest transactions.")
# You can add additional logic here if needed


#Function to send doge back
def send_doge_back():
    global creditsTotal
    dogeToSend = creditsTotal

    # Get the most recent sender address
    sender_address = get_input_address_of_latest_received_transaction(rpc_user, rpc_password, rpc_host, rpc_port)
    if not sender_address:
        print("No sender address found. Cannot proceed with sending Dogecoin.")
        return
    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_username}:{rpc_password}@localhost:22555')
        transaction_id = rpc_connection.sendtoaddress(sender_address, dogeToSend)
        print(f"Transaction sent. Transaction ID: {transaction_id}")

        # Resetting creditsTotal after successful transaction
        creditsTotal = 0


    except ConnectionRefusedError:
        print("Error sending transaction: [Errno 111] Connection refused")
    except Exception as e:
        print(f"Error while sending Dogecoin: {e}")


# Function to calc win
def calculate_win(results, bet_amount, payOutTable):
    global win, creditsTotal

    # Payout table parsing
    three_in_a_row = payOutTable['Three In A Row']
    four_in_a_row = payOutTable['Four In A Row']
    five_in_a_row = payOutTable['Five In A Row']
    in_any_reel = payOutTable['In Any Reel']

    # Initialize win to 0 for each calculation
    win = 0

    # Check for consecutive icons
    if results[0] == results[1] == results[2]:  # Three in a row
        win = three_in_a_row.get(results[0], 0) * bet_amount
        if len(results) > 3 and results[3] == results[0]:  # Four in a row
            win = four_in_a_row.get(results[0], 0) * bet_amount
            if len(results) > 4 and results[4] == results[0]:  # Five in a row
                win = five_in_a_row.get(results[0], 0) * bet_amount

    # Check for special icon in any reel
    reels_to_check = 3 if bet_amount == 3 else (4 if bet_amount == 6 else len(results))
    for icon in in_any_reel:
        if icon in results[:reels_to_check]:
            win += in_any_reel[icon] * bet_amount
            break  # Exit loop after finding the first occurrence

    # Update credits total
    creditsTotal += win
    print(win)

def update_bet_amount():
    global bet_amount
    # Update the bet amount as per your game's logic
    # Example: Cycling through 3, 6, 9
    bet_amount = (bet_amount % 9) + 3


def monitor_transactions():
    global creditsTotal, processed_tx_ids

    # Record the start time when the monitoring begins
    start_time = time.time()

    while True:
        time.sleep(30)  # Check for new transactions every 30 seconds

        try:
            response = send_rpc_request("listtransactions", ["*", 10])
            transactions = response.get('result', [])
            
            for tx in transactions:
                tx_time = tx['timereceived']  # Assuming 'timereceived' is in epoch time format

                # Process the transaction only if it's newer than the start time and not processed before
                if tx['category'] == 'receive' and tx_time > start_time and tx['txid'] not in processed_tx_ids:
                    creditsTotal += tx['amount']
                    processed_tx_ids.add(tx['txid'])  # Add to the set of processed transaction IDs
                    print(f"Received {tx['amount']} Dogecoin, Total Credits: {creditsTotal}")
        except Exception as e:
            print("Error:", e)




@app.route('/get_win_amount', methods=['GET'])
def get_win_amount():
    global win  # Use the global variable 'win'
    return jsonify({'winAmount': win})  # Return the 'win' variable


@app.route('/get_credits_total', methods=['GET'])
def get_credits_total():
    return jsonify({'creditsTotal': creditsTotal})


@app.route('/bet', methods=['POST'])
def bet():
    global isOperationInProgress
    # Check if an operation is already in progress
    if isOperationInProgress:
        return jsonify({"error": "Operation in progress"}), 429

    isOperationInProgress = True
    try:
        global bet_amount
        # Logic to update the bet amount
        update_bet_amount()  # Implement this function based on your logic

        return jsonify({'currentBetAmount': bet_amount})
    finally:
        # Ensure that the operation in progress flag is reset
        isOperationInProgress = False


@app.route('/addCredits', methods=["POST"])
def get_new_QR():
    global generated_address  # Declare the global variable
    generated_address = QR_gen.generate_and_print_qr_code()  # Assuming QR_gen can take a directory argument
    
    # Add credits to the user's account here
    time.sleep(5)
    # Signal JavaScript that QR code generation is complete
    response_data = {
        'message': 'QR code generated successfully',
        'generated_address': generated_address  # You can include the generated address in the response
    }
    
    return json.dumps(response_data), 200, {'Content-Type': 'application/json'}


@app.route('/spin', methods=['POST'])
def spin():
    global isOperationInProgress,creditsTotal, results
    # Check if an operation is already in progress
    if isOperationInProgress:
        return jsonify({"error": "Operation in progress"}), 429

    isOperationInProgress = True
    try:
        
        if creditsTotal >= bet_amount:
            creditsTotal -= bet_amount
            results = five_reel_value_gen.spin_reels()  # Call the function from the module

            # Load the payout table configuration
            payout_table_path = os.path.join(CONFIG_DIR, 'payOutTable.conf')
            if os.path.exists(payout_table_path) and os.path.getsize(payout_table_path) > 0:
                with open(payout_table_path, 'r') as file:
                    payOutTable = json.load(file)
                    calculate_win(results, bet_amount, payOutTable)
            else:
                print("Error: payOutTable.conf not found or is empty")
                return jsonify({"error": "payOutTable.conf not found or is empty"}), 500

            print(f"Spin results: {results}, New Credits Total: {creditsTotal}")
            return jsonify(message=results, newCreditsTotal=creditsTotal)
        else:
            return jsonify({"error": "Insufficient credits"}), 400

    finally:
        # Ensure that the operation in progress flag is reset
        isOperationInProgress = False


@app.route('/cashout', methods=['POST'])
def cash_out():
    global isOperationInProgress
    # Check if an operation is already in progress
    if isOperationInProgress:
        return jsonify({"error": "Operation in progress"}), 429

    isOperationInProgress = True
    try:
        print("Cash out button pressed")
        send_doge_back()  # Your existing function to process cash out
        return jsonify({"message": "Cash out button was pressed"}), 200
    finally:
        # Ensure that the operation in progress flag is reset
        isOperationInProgress = False




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    httpd = HTTPServer(('localhost', 8000), CORSHTTPRequestHandler)
    httpd.serve_forever()
    # Start the transaction monitoring in a separate thread
    threading.Thread(target=monitor_transactions, daemon=True).start()




