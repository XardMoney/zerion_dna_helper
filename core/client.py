import asyncio
import random

from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.exceptions import TransactionNotFound
from core.config import (ERC20_ABI, GAS_LIMIT_MULTIPLIER, GAS_PRICE_MULTIPLIER, SLIPPAGE, TOKENS_COINGECKO, TOKENS_PER_CHAIN, ZERION_DNA_ABI, ZERION_DNA_ADDRESS)
from utils.exceptions import BadWalletException, CoinGeckoRateLimitException


class Client:
    def __init__(self, wallet_name, private_key, proxy, network):
        self.network = network

        self.proxy = proxy
        self.request_kwargs = {"proxy": f'http://{proxy}', "verify_ssl": False} if proxy else {"verify_ssl": False}
        self.rpc = random.choice(self.network.rpc)
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc, request_kwargs=self.request_kwargs))

        self.wallet_name = wallet_name
        self.private_key = private_key

        try:
            self.address = AsyncWeb3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)

        except Exception as error:
            if "private key must be exactly" in str(error):
                raise BadWalletException(f'{self.private_key} <- Incorrect private key, wallet will be skipped')

            else:
                raise error

        self.session: ClientSession = ClientSession(
            connector=ProxyConnector.from_url(f'http://{proxy}', verify_ssl=False)
            if proxy else TCPConnector(verify_ssl=False)
        )

        self.contract = self.w3.eth.contract(ZERION_DNA_ADDRESS, abi=ZERION_DNA_ABI)

    @staticmethod
    def get_error_message(error):
        try:
            if isinstance(error.args[0], dict):
                error = error.args[0].get("message", error)

            return error

        except Exception:
            return error

    def change_network(self, network):
        self.network = network
        self.rpc = random.choice(network.rpc)
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc, request_kwargs=self.request_kwargs))

    async def get_contract(self, contract_address, abi=ERC20_ABI):
        return self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(contract_address),
            abi=abi
        )

    async def get_token_balance(self, token_name):
        if token_name and token_name != self.network.token:
            contract = await self.get_contract(TOKENS_PER_CHAIN[self.network.name][token_name])
            amount_in_wei = await contract.functions.balanceOf(self.address).call()

        else:
            amount_in_wei = await self.w3.eth.get_balance(self.address)

        return amount_in_wei

    async def get_decimals(self, token_name):
        if token_name != self.network.token:
            contract = await self.get_contract(TOKENS_PER_CHAIN[self.network.name][token_name])
            return await contract.functions.decimals().call()

        else:
            return 18

    async def get_priotiry_fee(self):
        fee_history = await self.w3.eth.fee_history(5, "latest", [20.0])
        non_empty_block_priority_fees = [fee[0] for fee in fee_history["reward"] if fee[0] != 0]
        divisor_priority = max(len(non_empty_block_priority_fees), 1)
        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))

        return priority_fee

    async def prepare_transaction(self, value=0):
        tx_params = {
            "chainId": self.network.chain_id,
            "from": self.w3.to_checksum_address(self.address),
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value
        }

        if self.network.eip1559_support:

            base_fee = await self.w3.eth.gas_price
            max_priority_fee_per_gas = await self.get_priotiry_fee()
            max_fee_per_gas = int(base_fee + max_priority_fee_per_gas * 1.05 * GAS_PRICE_MULTIPLIER)

            if self.network.name == ["Scroll", "Optimism"]:
                max_fee_per_gas = int(max_fee_per_gas / GAS_PRICE_MULTIPLIER * 1.1)

            if max_priority_fee_per_gas > max_fee_per_gas:
                max_priority_fee_per_gas = int(max_fee_per_gas * 0.95)

            tx_params["maxPriorityFeePerGas"] = max_priority_fee_per_gas
            tx_params["maxFeePerGas"] = int(max_fee_per_gas * 1.2)
            tx_params["type"] = "0x2"

        else:

            if self.network.name == "BNB Chain":
                tx_params["gasPrice"] = self.w3.to_wei(round(random.uniform(1.4, 1.5), 1), "gwei")

            else:
                gas_price = await self.w3.eth.gas_price

                if self.network.name == ["Scroll", "Optimism"]:
                    gas_price = int(gas_price / GAS_PRICE_MULTIPLIER * 1.1)

                tx_params["gasPrice"] = int(gas_price * 1.2 * GAS_PRICE_MULTIPLIER)

        return tx_params

    async def send_transaction(self, tx, timeout=360, poll_latency=5):
        try:
            tx["gas"] = int((await self.w3.eth.estimate_gas(tx)) * GAS_LIMIT_MULTIPLIER)
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key).rawTransaction
            tx_hash = self.w3.to_hex(await self.w3.eth.send_raw_transaction(signed_tx))

        except Exception as error:
            raise Exception(f'{self.get_error_message(error)}')

        total_time = 0
        while True:
            try:
                tx_receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
                status = tx_receipt.get("status")

                if status == 1:
                    return f'{self.network.explorer}tx/{tx_hash}'

                elif status is None:
                    total_time += poll_latency
                    await asyncio.sleep(poll_latency)

                else:
                    raise Exception(f'{self.network.explorer}tx/{tx_hash}')

            except TransactionNotFound:
                if total_time > timeout:
                    raise Exception(f'Transaction is not in the chain after {timeout} seconds')

                total_time += poll_latency
                await asyncio.sleep(poll_latency)

            except Exception as error:
                if "Transaction failed" in str(error):
                    raise Exception(f'{self.network.explorer}tx/{tx_hash}')

                total_time += poll_latency
                await asyncio.sleep(poll_latency)

    async def make_approve(self, token_name, spender_address):
        tx = await (await self.get_contract(TOKENS_PER_CHAIN[self.network.name][token_name])).functions.approve(
            self.w3.to_checksum_address(spender_address),
            2**256 - 1).build_transaction(await self.prepare_transaction())
        tx_url = await self.send_transaction(tx)
        return tx_url

    async def get_token_price(self, token_name, currency="usd"):

        stables = [
            "tether",
            "usd-coin",
        ]

        if token_name in stables:
            return 1.0

        await asyncio.sleep(10)
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            "ids": f'{token_name}',
            "vs_currencies": f'{currency}'
        }

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return float(data[token_name][currency])

            elif response.status == 429:
                raise CoinGeckoRateLimitException

            raise Exception(f'Bad request to CoinGecko API: {response.status}')

    async def price_impact_defender(self, from_token_name, to_token_name, from_token_amount, to_token_amount):
        from_token_amount_in_usd = (await self.get_token_price(TOKENS_COINGECKO[from_token_name])) * from_token_amount
        to_token_amount_in_usd = (await self.get_token_price(TOKENS_COINGECKO[to_token_name])) * to_token_amount
        actual_slippage = 100 - (to_token_amount_in_usd / from_token_amount_in_usd) * 100

        if actual_slippage > SLIPPAGE:
            raise Exception(
                f'Actual slippage > your wanted slippage ({actual_slippage:.3}% > {SLIPPAGE}%)'
            )
