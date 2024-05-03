from core.config import *
from utils.log import log
import asyncio
import random


class ZerionClient:

    def __init__(self):
        pass

    @staticmethod
    async def check_gas(w3, wallet):
        while True:
            try:
                gas = round(w3.from_wei(await w3.eth.gas_price, "gwei"), 1)

                if gas <= GWEI_LIMIT:
                    log.success(f'{wallet.address} | Check gas | GWEI: {gas} | Limit hasn\'t been exceeded')
                    return True

                else:
                    log.warning(f'{wallet.address} | Check gas | GWEI: {gas} | Limit has been exceeded, waiting...')
                    await asyncio.sleep(random.randint(*SLEEP_RANGE_FOR_GWEI_CHECKS))

            except Exception:
                continue

    async def mint_zerion_dna(self, w3, wallet, retry=1):
        await self.check_gas(w3, wallet)
        try:
            tx = {
                "from": wallet.address,
                "to": DNA_ADDRESS,
                "value": 0,
                "nonce": await w3.eth.get_transaction_count(wallet.address),
                "data": "0x1249c58b",
                "chainId": await w3.eth.chain_id,
                "maxFeePerGas": int(await w3.eth.gas_price * 1.2),
                "maxPriorityFeePerGas": int(await w3.eth.gas_price)
            }
            tx["gas"] = await w3.eth.estimate_gas(tx)
            sign = wallet.sign_transaction(tx)
            tx_hash = await w3.eth.send_raw_transaction(sign.rawTransaction)
            log.info(f'{wallet.address} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                     f'Transaction sent')
            tx_receipt = await w3.eth.wait_for_transaction_receipt(tx_hash, timeout=150)

            if tx_receipt.status == 1:

                log.success(f'{wallet.address} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                            f'Transaction succeeded | {SCAN_URL}{w3.to_hex(tx_hash)}')
                return True

            else:
                log.error(f'{wallet.address()} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                          f'Transaction failed')
                retry += 1

                if retry > NUMBER_OF_RETRIES:
                    log.critical(f'{wallet.address()} | Wallet failed after {NUMBER_OF_RETRIES} '
                                 f'{"retries" if NUMBER_OF_RETRIES > 1 else "retry"}')
                    return False

                await asyncio.sleep(random.randint(*SLEEP_RANGE))
                return await self.mint_zerion_dna(w3, wallet, retry)

        except Exception as error:
            log.error(f'{wallet.address()} | Mint Zerion DNA | Attempt {retry}/{NUMBER_OF_RETRIES} | '
                      f'Error: {error}')
            retry += 1

            if retry > NUMBER_OF_RETRIES:
                log.critical(f'{wallet.address()} | Wallet failed after {NUMBER_OF_RETRIES} '
                             f'{"retries" if NUMBER_OF_RETRIES > 1 else "retry"}')
                return False

            await asyncio.sleep(random.randint(*SLEEP_RANGE))
            return await self.mint_zerion_dna(w3, wallet, retry)
