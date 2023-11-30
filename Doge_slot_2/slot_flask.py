from bitcoinrpc.authproxy import AuthServiceProxy
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import five_reel_value_gen
import win_calculator
from get_slot_address import check_and_update_slot_address
from qr_generator import generate_qr_without_text
from apscheduler.schedulers.background import BackgroundScheduler
from transaction_listener import check_incoming_transactions
import time
import math

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# Global variables
bet_amount = 0  # Initial default value
credits = 0
win = 0
results = []
input_address = None
slot_address = None
txid_list = []


@app.route('/get-slot-address')
def get_slot_address():
    # You might want to add logic here to retrieve or generate slot_address
    return jsonify({'slot_address': slot_address})

@app.route('/get-reel-results')
async def get_reel_results():
    global results, win, credits
    # Call the function from five_reel_value_gen to get new results
    credits = credits - bet_amount
    time.sleep(1)
    results = five_reel_value_gen.spin_reels()
    win, credits = win_calculator.calculate_win(results, bet_amount, credits)
    return jsonify(results)

@app.route('/get-credits')
async def get_credits():
    global credits
    return jsonify({'credits': credits})  # Correctly returning the credits

@app.route('/get-win')
async def git_win():
    global win
    return jsonify({'win': win})

@app.route('/input-address')
async def get_input_address():
    global input_address
    return jsonify({'input_address': input_address})  # Correctly returning the credits

@app.route('/get-bet')
def get_bet():
    global bet_amount
    try:
        return jsonify({'bet': bet_amount})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/change-bet', methods=['POST'])
def bet():
    global bet_amount
    update_bet_amount()  # Update the bet amount
    return jsonify({'currentBetAmount': bet_amount})

def update_bet_amount():
    global bet_amount
    # Cycle through the bet amounts 3, 6, 9
    if bet_amount == 3:
        bet_amount = 6
    elif bet_amount == 6:
        bet_amount = 9
    else:
        bet_amount = 3

def update_credits():
    global credits, last_checked, slot_address, input_address
    new_credits, new_input_address = check_unconfirmed_transactions(slot_address, last_checked)  # Get both credits and input address
    if new_credits > 0:
        credits += math.floor(new_credits)  # Round down to the nearest integer
        input_address = new_input_address  # Update the global input_address
        last_checked = time.time()
        print(input_address)

slot_address = check_and_update_slot_address()

def check_incoming_transactions_periodically():
    global txid_list, credits, input_address
    print("Checking for incoming transactions...")
    amount, new_input_address, txid = check_incoming_transactions(slot_address)

    # Ensure that amount is an integer (or can be converted to an integer)
    if amount is not None:
        try:
            amount = int(amount)  # Convert amount to integer
        except ValueError:
            print("Invalid amount format. Unable to convert to integer.")
            return

        # Check if amount is greater than 0
        if amount > 0:
            print(f"Received {amount} from {new_input_address}. Transaction ID: {txid}")

            # Check if the transaction ID is new
            if txid not in txid_list:
                # Update credits and add the transaction ID to the list
                credits += amount
                txid_list.append(txid)

                # Update the input address
                input_address = new_input_address
            else:
                print("Transaction already processed.")
        else:
            print("No new transactions found or error occurred.")
    else:
        print("Amount is None. No new transactions to process.")

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_incoming_transactions_periodically, trigger="interval", seconds=10)

# Start the scheduler
scheduler.start()

generate_qr_without_text(slot_address)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    


    