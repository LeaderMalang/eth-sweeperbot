from web3 import Web3
import time
import sys

# Constants
ETH_MIN_SWEEP = '0.002'  # ETH MIN SWEEP
WALLET_SWEEP_KEY = '3ff61cb8f6370f010475abdd3776da2c13c1053e9948a5422cf7506dd5944bf2'
WEB3_PROVIDER = 'https://us-ethereum1.twnodes.com/'  # Trust Wallet Node

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Wallets
WALLET_SWEEP = web3.to_checksum_address('0x947a1eA3a5B18A5065fd9d55663505806eaa9DDC')
WALLET_DEST = web3.to_checksum_address('0x1ae97b609C30134b8A3b992581b29096Deb28dBb')

# Minimum sweep threshold in wei
ETH_MIN = web3.to_wei(ETH_MIN_SWEEP, 'ether')

# Progress printing
def print_progress(progress):
    sys.stdout.write('\r' + progress)
    sys.stdout.flush()

# Sleep function
def sleep(minutes):
    time.sleep(minutes * 60)

# Main function
def main():
    counter = 0
    done = 0
    errors = 0

    while True:
        counter += 1
        text = f"A: {done} / E: {errors} / Checked: {counter} / Balance: "

        # Get wallet balance
        balance = web3.eth.get_balance(WALLET_SWEEP)

        if balance > ETH_MIN:
            try:
                # Get nonce for the wallet
                nonce = web3.eth.get_transaction_count(WALLET_SWEEP)

                # Estimate gas for the transaction
                transaction = {
                    'to': WALLET_DEST,
                    'value': balance,
                    'gas': 21000,  # Set a default gas limit, will adjust later
                    'gasPrice': web3.eth.gas_price,  # Current gas price from network
                    'nonce': nonce,
                    'chainId': 1  # Ethereum mainnet chain ID
                }

                # Estimate gas needed
                gas_limit = web3.eth.estimate_gas(transaction)
                gas_price = web3.eth.gas_price  # Get the current gas price in wei

                # Calculate transfer amount after gas fee
                transfer_amount = balance - gas_price * gas_limit

                # Update transaction with calculated values
                tx_price = {
                    'chainId': 1,
                    'nonce': nonce,
                    'to': WALLET_DEST,
                    'value': transfer_amount,
                    'gas': gas_limit,
                    'gasPrice': gas_price
                }

                # Sign the transaction
                signed_tx = web3.eth.account.sign_transaction(tx_price, WALLET_SWEEP_KEY)

                # Send the signed transaction
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

                # Calculate the sent amount in ETH
                amount_sent_eth = web3.from_wei(transfer_amount, 'ether')
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

                print(f"amount transfered {amount_sent_eth} Transaction successful with hash: {web3.to_hex(tx_hash)}")
                done += 1
                sleep(60)  # Wait for 60 minutes before next attempt

            except Exception as e:
                sleep(10)  # Wait for 10 minutes on error
                print(e)
                errors += 1
        else:
            # Convert balance to ETH for display
            balance_eth = web3.from_wei(balance, 'ether')
            text += f"{balance_eth} ETH"

        # Update progress
        print_progress(text)

if __name__ == "__main__":
    main()
