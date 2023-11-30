import os
import json


# Function to load the payout table
def load_payout_table():
    try:
        with open('pay_out_table.conf', 'r') as file:
            return json.load(file)
    except Exception as e:
        print("Error loading payout table:", e)
        return None  # Return None if there's an error

# Load the payout table
payOutTable = load_payout_table()
if payOutTable is None:
    print("Failed to load payout table. Exiting.")
    exit(1)  # Exit if the payout table cannot be loaded

# Function to calculate win
def calculate_win(results, bet_amount, credits):
    global payOutTable

    print("Calculating win for:", results, "Bet amount:", bet_amount, "Credits:", credits)

    # Check if credits are sufficient for the bet
    if credits + bet_amount < bet_amount:
        print("Insufficient credits for the bet.")
        return 0, credits  # Return 0 win and current credits

    # Initialize win to 0 for each calculation
    win = 0

    try:
        # Check for consecutive icons
        if results[0] == results[1] == results[2]:  # Three in a row
            win = payOutTable['Three In A Row'].get(results[0], 0) * bet_amount
            if len(results) > 3 and results[3] == results[0]:  # Four in a row
                win = payOutTable['Four In A Row'].get(results[0], 0) * bet_amount
                if len(results) > 4 and results[4] == results[0]:  # Five in a row
                    win = payOutTable['Five In A Row'].get(results[0], 0) * bet_amount

        # Check for special icon in any reel
        reels_to_check = 3 if bet_amount == 3 else (4 if bet_amount == 6 else len(results))
        for icon in payOutTable['In Any Reel']:
            if icon in results[:reels_to_check]:
                win += payOutTable['In Any Reel'][icon] * bet_amount
                break  # Exit loop after finding the first occurrence

        # Update credits total
        credits += win
        print("Win:", win, "Updated Credits:", credits)
        return win, credits
    except Exception as e:
        print("Error during win calculation:", e)
        return 0, credits  # Return default values in case of error


