from web3 import AsyncWeb3

from core.config import (
    GWEI_LIMIT, SLEEP_RANGE_FOR_GWEI_CHECKS, DNA_ADDRESS, NUMBER_OF_RETRIES, SCAN_URL, RPC_URLS, DNA_ABI
)
from settings import SLEEP_RANGE_BETWEEN_ATTEMPT
from utils.log import log
import asyncio
import random


class ZerionClient:

    def __init__(self, chain_name: str, private_key: str, proxy: str = None):
        self.chain_name = chain_name
        self.private_key = private_key
        self.proxy = proxy
        self.proxy_url = proxy.split("@")[1] if self.proxy else None
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(random.choice(RPC_URLS), request_kwargs={
            "proxy": proxy,
            "timeout": 60
        }))
        self.wallet = self.w3.eth.account.from_key(private_key)

    @property
    def address(self) -> str:
        return self.wallet.address

    async def check_gas(self):
        while True:
            try:
                gas = round(self.w3.from_wei(await self.w3.eth.gas_price, "gwei"), 1)

                if gas <= GWEI_LIMIT:
                    log.success(f'{self.address} | Check gas | GWEI: {gas} | Limit hasn\'t been exceeded')
                    return True

                else:
                    log.warning(f'{self.address} | Check gas | GWEI: {gas} | Limit has been exceeded, waiting...')
                    await asyncio.sleep(random.randint(*SLEEP_RANGE_FOR_GWEI_CHECKS))

            except Exception:
                continue

    async def check_minted(self, retry=1):
        contract = self.w3.eth.contract(DNA_ADDRESS, abi=DNA_ABI)
        try:
            balance = await contract.functions.balanceOf(self.address).call()
            if balance > 0:
                return True

            return False
        except Exception as error:
            log.error(f'{self.address} | Check minted Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                      f'Error: {error}')
            retry += 1

            if retry > NUMBER_OF_RETRIES:
                log.critical(f'{self.address} | Wallet failed after {NUMBER_OF_RETRIES} '
                             f'{"retries" if NUMBER_OF_RETRIES > 1 else "retry"}')
                return False

            sleep_time = random.randint(*SLEEP_RANGE_BETWEEN_ATTEMPT)
            log.info(f'Sleeping: {sleep_time} second')
            await asyncio.sleep(sleep_time)
            return await self.mint_zerion_dna(retry)

    async def mint_zerion_dna(self, retry=1):
        log.success(f'[{self.address}] | Start mint Zerion DNA!')
        await self.check_gas()
        if await self.check_minted():
            log.warning(f'[{self.address}] | DNA already minted!')
            return False

        try:
            tx = {
                "from": self.address,
                "to": DNA_ADDRESS,
                "value": 0,
                "nonce": await self.w3.eth.get_transaction_count(self.address),
                "data": "0x1249c58b",
                "chainId": await self.w3.eth.chain_id,
                "maxFeePerGas": int(await self.w3.eth.gas_price * 1.2),
                "maxPriorityFeePerGas": int(await self.w3.eth.gas_price)
            }
            tx["gas"] = await self.w3.eth.estimate_gas(tx)
            sign = self.wallet.sign_transaction(tx)
            tx_hash = await self.w3.eth.send_raw_transaction(sign.rawTransaction)
            log.info(f'{self.wallet.address} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                     f'Transaction sent')
            tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

            if tx_receipt.status == 1:
                log.success(f'{self.address} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                            f'Transaction succeeded | {SCAN_URL}{self.w3.to_hex(tx_hash)}')
                return True

            else:
                raise Exception("Transaction failed")

        except Exception as error:
            if 'insufficient funds for transfer' in str(error):
                log.error('insufficient funds for transfer!')
                return False

            log.error(f'{self.address} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                      f'Error: {error}')
            retry += 1

            if retry > NUMBER_OF_RETRIES:
                log.critical(f'{self.address} | Wallet failed after {NUMBER_OF_RETRIES} '
                             f'{"retries" if NUMBER_OF_RETRIES > 1 else "retry"}')
                return False

            sleep_time = random.randint(*SLEEP_RANGE_BETWEEN_ATTEMPT)
            log.info(f'Sleeping: {sleep_time} second')
            await asyncio.sleep(sleep_time)
            return await self.mint_zerion_dna(retry)
