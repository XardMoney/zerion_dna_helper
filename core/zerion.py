import json
import random

from core.client import Client
from core.config import (AMOUNT_PERCENT, TOKENS_ZERION, ZERION_DNA_ABI, ZERION_DNA_ADDRESS)
from utils.decorators import check_gas, retry
from utils.log import Logger


class Zerion(Client, Logger):
    def __init__(self, wallet_name, private_key, proxy, network):
        Client.__init__(self, wallet_name, private_key, proxy, network)
        Logger.__init__(self)

    @retry
    async def check_presence_of_dna(self):
        msg = "Starting to check for the presence of the DNA"
        self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__,
                     self.check_presence_of_dna.__name__, msg)

        contract = await self.get_contract(ZERION_DNA_ADDRESS, ZERION_DNA_ABI)
        amount = await contract.functions.balanceOf(self.address).call()

        if amount > 0:
            msg = "DNA has already been minted"
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__,
                         self.check_presence_of_dna.__name__, msg, "success")

        else:
            msg = "DNA hasn't minted yet"
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__,
                         self.check_presence_of_dna.__name__, msg, "warning")

        return amount

    @retry
    @check_gas
    async def mint_dna(self):
        msg = "Starting to mint the DNA"
        self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.mint_dna.__name__, msg)
        tx = {
            "to": ZERION_DNA_ADDRESS,
            "data": "0x1249c58b",
        }
        tx.update(await self.prepare_transaction())
        tx_url = await self.send_transaction(tx)

        if tx_url:
            msg = f'Successfully minted the DNA: {tx_url}'
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.mint_dna.__name__, msg,
                         "success")
            return True

    async def get_auto_data_for_swap(self, from_token_name, to_token_name):
        if from_token_name != self.network.token:
            from_token_amount_in_wei = await self.get_token_balance(from_token_name)

        else:
            from_token_amount_in_wei = int(await self.get_token_balance(from_token_name) *
                                           (random.uniform(*AMOUNT_PERCENT) / 100))

        to_token_amount_in_wei = await self.get_token_balance(to_token_name)
        return from_token_amount_in_wei, to_token_amount_in_wei

    async def get_best_offer(self, from_token_name, to_token_name, from_token_amount_in_wei):
        url = f'https://transactions.zerion.io/swap/quote/stream?' \
              f'input_token={TOKENS_ZERION[from_token_name]}&' \
              f'output_token={TOKENS_ZERION[to_token_name]}&' \
              f'input_chain={self.network.input_chain_name}&' \
              f'input_amount={from_token_amount_in_wei}&' \
              f'slippage=0.1&' \
              f'from={self.address}'

        stream = {}

        async with self.session.get(url=url) as response:
            events = [line.strip().decode() async for line in response.content if line.strip()]

        for i in range(0, len(events) - 1, 2):
            event = events[i:i + 2]

            if event[0].split(maxsplit=1)[1] == "update":

                if "offer" in stream:
                    stream["offer"] = max(stream["offer"], json.loads(event[1].split(maxsplit=1)[1])[0],
                                          key=lambda offer: (offer["enough_balance"], offer["enough_allowance"],
                                                             offer["output_amount_min"]))

                else:
                    stream["offer"] = json.loads(event[1].split(maxsplit=1)[1])[0]

            elif event[0].split(maxsplit=1)[1] == "exception":
                raise Exception(event[1].split(maxsplit=1)[1])

        if not ("offer" in stream):
            raise Exception("No offers for swap")

        return stream["offer"]

    @retry
    @check_gas
    async def swap(self, from_token_name, to_token_name):
        msg = f"Starting to swap {from_token_name} to {to_token_name}"
        self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.swap.__name__, msg)
        data = await self.get_auto_data_for_swap(from_token_name, to_token_name)
        offer = await self.get_best_offer(from_token_name, to_token_name, data[0])

        if not (offer["enough_allowance"]):
            msg = f'Not enough allowance of {from_token_name}'
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.swap.__name__, msg,
                         "warning")
            msg = f'Starting to approve {from_token_name}'
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.swap.__name__, msg)
            tx_url = await self.make_approve(from_token_name, offer["token_spender"])
            msg = f'Successfully approved {from_token_name}: {tx_url}'
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.swap.__name__, msg,
                         "success")
            offer = await self.get_best_offer(from_token_name, to_token_name, data[0])

        from_token_decimals = await self.get_decimals(from_token_name)
        to_token_decimals = await self.get_decimals(to_token_name)
        from_token_amount = round(int(offer["input_amount_max"]) / 10 ** from_token_decimals, 8)
        to_token_amount = round(int(offer["output_amount_min"]) / 10 ** to_token_decimals, 8)
        await self.price_impact_defender(from_token_name, to_token_name, from_token_amount, to_token_amount)
        tx = {
            "to": offer["token_spender"],
            "data": offer["transaction"]["data"]
        }
        tx.update(await self.prepare_transaction(int(offer["transaction"]["value"])))
        tx_url = await self.send_transaction(tx)
        msg = f'Successfully swapped ' \
              f'{from_token_amount} {from_token_name} to ' \
              f'a minimum of {to_token_amount} {to_token_name}: {tx_url}'
        self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, self.swap.__name__, msg,
                     "success")
        return True
