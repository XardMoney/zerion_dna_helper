from utils.networks import *

'-----------------------------------------------GENERAL SETTINGS-------------------------------------------------------'
# Shuffle accounts (True or False)
SHUFFLE_ACCOUNTS = True

# Limit of accounts that can be run concurrently
SEMAPHORE_LIMIT = 10

# Limit of retries for all the actions
NUMBER_OF_ATTEMPTS = 7

# Range of the seconds to sleep between actions (random selection)
SLEEP_RANGE = [15, 25]

'-------------------------------------------------GAS CONTROL----------------------------------------------------------'
# Use gas control (True or False)
GAS_CONTROL = True

# Limit of GWEI (Ethereum) for all the transactions if gas control is enabled
GWEI_LIMIT = 20

# Range of the seconds to sleep between gwei checks (random selection)
SLEEP_RANGE_FOR_GWEI_CHECKS = [40, 60]

'------------------------------------------------SWAP CONTROL----------------------------------------------------------'
# Number of full swaps, i.e. ETH -> USDC -> ETH is 1 iteration
ITERATIONS = [7, 12]

# Balance percent of native token that will be used for swaps
AMOUNT_PERCENT = [50, 75]

# Maximum total slippage for swap, including price impact and Zerion fees (recommended value - 2%)
SLIPPAGE = 2

# Choose networks that will be used for swaps: Ethereum, ZkSync, Optimism, Base, Arbitrum (random selection)
NETWORKS_FOR_SWAP = [Ethereum, ZkSync, Optimism, Base, Arbitrum]

'------------------------------------------------DATA CONTROL----------------------------------------------------------'
# Path to file with the accounts data (if unsure, leave the option at the default)
EXCEL_FILE_PATH = "files/accounts.xlsx"

# Name of page with the accounts data (if unsure, leave the option at the default)
EXCEL_PAGE_NAME = "data"
