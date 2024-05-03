from settings import SEMAPHORE_LIMIT, NUMBER_OF_RETRIES, SLEEP_RANGE, GWEI_LIMIT, SLEEP_RANGE_FOR_GWEI_CHECKS
from web3 import Web3
import asyncio

SEMAPHORE_LIMIT = max(int(SEMAPHORE_LIMIT), 1)

NUMBER_OF_RETRIES = max(int(NUMBER_OF_RETRIES), 1)

SLEEP_RANGE = sorted(([max(int(x), 1) for x in SLEEP_RANGE] * 2)[:2])

GWEI_LIMIT = max(int(GWEI_LIMIT), 1)

SLEEP_RANGE_FOR_GWEI_CHECKS = sorted(([max(int(x), 1) for x in SLEEP_RANGE_FOR_GWEI_CHECKS] * 2)[:2])

FILE_LOCK = asyncio.Lock()

RPC_URLS = ["https://ethereum.publicnode.com", "https://1rpc.io/eth", "https://rpc.ankr.com/eth"]

SCAN_URL = "https://etherscan.io/tx/"

DNA_ADDRESS = Web3.to_checksum_address("0x932261f9Fc8DA46C4a22e31B45c4De60623848bF")
