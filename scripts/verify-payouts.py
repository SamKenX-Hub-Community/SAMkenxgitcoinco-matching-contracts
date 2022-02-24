"""
A modified version script will be used in gitcoinco/web repository to facilitate match payouts
using the production data
"""

import json
from decimal import Decimal
from web3 import Web3

# ========================================= CONFIGURATION ==========================================

# Read our expected data
with open('outputs/payouts.json') as f:
  expected_payouts = json.load(f)

# Provider URL
PROVIDER = 'ws://127.0.0.1:8545/'

# Contract addresses
match_payouts_address = '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512' # deterministic on localhost
token_address = '0x5FbDB2315678afecb367f032d93F642f64180aa3' # deterministic on localhost

# Filters for finding events
from_block = 0 # block contract was deployed at

# =========================================== CONSTANTS ============================================

SCALE = Decimal(1e18)
match_payouts_abi = '[ { "inputs": [ { "internalType": "address", "name": "_owner", "type": "address" }, { "internalType": "address", "name": "_funder", "type": "address" }, { "internalType": "contract IERC20", "name": "_dai", "type": "address" } ], "stateMutability": "nonpayable", "type": "constructor" }, { "anonymous": false, "inputs": [], "name": "Finalized", "type": "event" }, { "anonymous": false, "inputs": [], "name": "Funded", "type": "event" }, { "anonymous": false, "inputs": [], "name": "FundingWithdrawn", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "PayoutAdded", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "PayoutClaimed", "type": "event" }, { "inputs": [ { "internalType": "address", "name": "_recipient", "type": "address" } ], "name": "claimMatchPayout", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "dai", "outputs": [ { "internalType": "contract IERC20", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "enablePayouts", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "finalize", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "funder", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "owner", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "payouts", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "components": [ { "internalType": "address", "name": "recipient", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "internalType": "struct MatchPayouts.PayoutFields[]", "name": "_payouts", "type": "tuple[]" } ], "name": "setPayouts", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "state", "outputs": [ { "internalType": "enum MatchPayouts.State", "name": "", "type": "uint8" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "withdrawFunding", "outputs": [], "stateMutability": "nonpayable", "type": "function" } ]'
erc20_abi = '[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_subtractedValue","type":"uint256"}],"name":"decreaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_addedValue","type":"uint256"}],"name":"increaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"payable":false,"stateMutability":"nonpayable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

# ========================================= MAIN EXECUTION =========================================

# Get expected total match amount
expected_total_tokens_amount = Decimal(0)
for (index,payout) in enumerate(expected_payouts):
  expected_total_tokens_amount += Decimal(payout['amount'])
expected_total_tokens_amount = expected_total_tokens_amount / SCALE

# Get contract instances
w3 = Web3(Web3.WebsocketProvider(PROVIDER))
match_payouts = w3.eth.contract(address=match_payouts_address, abi=match_payouts_abi)
token = w3.eth.contract(address=token_address, abi=erc20_abi)

# Get PayoutAdded events
payout_added_filter = match_payouts.events.PayoutAdded.createFilter(fromBlock=from_block)
payout_added_logs = payout_added_filter.get_all_entries() # print these if you need to inspect them

# Sort payout logs by ascending block number, this way if a recipient appears in multiple blocks
# we use the value from the latest block
sorted_payout_added_logs = sorted(payout_added_logs, key=lambda log:log['blockNumber'], reverse=False)

# Get total required token balance based on PayoutAdded events. Events will be sorted chronologically,
# so if a recipient is duplicated we only keep the latest entry. We do this by storing our own
# mapping from recipients to match amount and overwriting it as needed just like the contract would.
# We keep another dict that maps the recipient's addresses to the block it was found in. If we find
# two entries for the same user in the same block, we throw, since we don't know which is the
# correct one
payment_dict = {}
user_block_dict = {}
for log in sorted_payout_added_logs:
  # Parse parameters from logs
  recipient = log['args']['recipient']
  amount = Decimal(log['args']['amount'])
  block = log['blockNumber']

  # Check if recipient's payout has already been set in this block
  if recipient in user_block_dict and user_block_dict[recipient] == block:
    raise Exception(f'Recipient {recipient} payout was set twice in block {block}, so unclear which to use')

  # Recipient not seen in this block, so save data
  payment_dict[recipient] = amount
  user_block_dict[recipient] = block

# Sum up each entry to get the total required amount
total_tokens_required_wei = sum(payment_dict[recipient] for recipient in payment_dict.keys())

# Convert to human units
total_tokens_required = total_tokens_required_wei / SCALE 

# Verify that total tokens required (from event logs) equals the expected amount
if expected_total_tokens_amount != total_tokens_required:
  print('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
  print('Total token payout amount in the contract does not equal the expected value!')
  print('  Total expected amount:  ', expected_total_tokens_amount)
  print('  Total amount from logs: ', total_tokens_required)
  print('* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n')
  raise Exception('Total payout amount in the contract does not equal the expected value!')
print('Total payout amount in the contracts is the expected value')

# Get contract tokens balance
token_balance = Decimal(token.functions.balanceOf(match_payouts_address).call()) / SCALE

# Verify that contract has sufficient Tokens balance to cover all payouts
print('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
if token_balance == total_tokens_required:
  print(f'Contract balance of {token_balance} tokens is exactly equal to the required amount')

elif token_balance < total_tokens_required:
  shortage = total_tokens_required - token_balance
  print('Contract Tokens balance is insufficient')
  print('  Required balance: ', total_tokens_required)
  print('  Current balance:  ', token_balance)
  print('  Extra Tokens needed: ', shortage)
  print(f'\n Contract needs another {shortage} tokens')

elif token_balance > total_tokens_required:
  excess = token_balance - total_tokens_required
  print('Contract has excess Tokens balance')
  print('  Required balance:  ', total_tokens_required)
  print('  Current balance:   ', token_balance)
  print('  Excess Tokens amount: ', excess)
  print(f'\n Contract has an excess of {excess} tokens')
print('* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n')
