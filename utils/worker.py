import asyncio
import random

import pandas as pd

from core.config import (EXCEL_FILE_PATH, EXCEL_PAGE_NAME, NETWORKS_FOR_SWAP, SEMAPHORE_LIMIT, SHUFFLE_ACCOUNTS,
                         SLEEP_RANGE, ITERATIONS, TOKENS_PER_CHAIN)
from core.zerion import Zerion
from utils.exceptions import BadWalletException, NoMoreAttemptsException
from utils.log import Logger
from utils.networks import Ethereum


class Worker(Logger):
    def __init__(self):
        Logger.__init__(self)

    async def get_accounts_data(self):
        try:
            with open(EXCEL_FILE_PATH, "rb") as file:
                wb = pd.read_excel(file, sheet_name=EXCEL_PAGE_NAME)
                accounts_data = []

                for index, row in wb.iterrows():
                    account_name = row["Name"]
                    private_key = row["Private Key"]
                    proxy = row["Proxy"]

                    if pd.isnull(private_key):
                        continue

                    else:
                        private_key = str(private_key).strip()

                    if pd.isnull(proxy):
                        proxy = ""

                    else:
                        proxy = str(proxy).strip()

                    if pd.isnull(account_name):
                        account_name = f'Wallet {index + 1}'

                    else:
                        account_name = str(account_name).strip()

                    accounts_data.append((account_name, private_key, proxy))

                return accounts_data

        except Exception as error:
            self.log_msg(msg=f'Error while getting accounts data: {error}', msg_type="critical")
            exit()

    async def check_presence_of_dna_task(self, wallet_name, private_key, proxy):
        zerion = Zerion(wallet_name, private_key, proxy, Ethereum)
        try:
            if await zerion.check_presence_of_dna() == 0:
                return False

            else:
                return True

        except NoMoreAttemptsException as error:
            self.log_msg(wallet_name, Ethereum, zerion.__class__.__name__, zerion.swap.__name__, error, "error")
            return False

        finally:
            await zerion.session.close()

    async def mint_dna_task(self, wallet_name, private_key, proxy):
        zerion = Zerion(wallet_name, private_key, proxy, Ethereum)

        try:
            await zerion.mint_dna()
            return True

        except NoMoreAttemptsException as error:
            self.log_msg(wallet_name, Ethereum, zerion.__class__.__name__, zerion.swap.__name__, error, "error")
            return False

        finally:
            await zerion.session.close()

    async def full_swap_task(self, wallet_name, private_key, proxy):
        network = random.choice(NETWORKS_FOR_SWAP)
        zerion = Zerion(wallet_name, private_key, proxy, network)
        x_token_name = network.token
        y_token_name = random.choice([token for token in TOKENS_PER_CHAIN[network.name] if token != network.token])

        try:
            await zerion.swap(x_token_name, y_token_name)
            await asyncio.sleep(random.uniform(*SLEEP_RANGE))
            await zerion.swap(y_token_name, x_token_name)
            return True

        except NoMoreAttemptsException as error:
            self.log_msg(wallet_name, network, zerion.__class__.__name__, zerion.swap.__name__, error, "error")
            return False

        finally:
            await zerion.session.close()

    async def run_wallet(self, semaphore, sleep_needed, wallet_name, private_key, proxy):
        async with semaphore:
            if sleep_needed:
                await asyncio.sleep(random.randint(*SLEEP_RANGE))

            try:
                iterations = random.randint(*ITERATIONS)
                presence_of_dna = await self.check_presence_of_dna_task(wallet_name, private_key, proxy)

                if not presence_of_dna:
                    await self.mint_dna_task(wallet_name, private_key, proxy)

                    if iterations > 0:
                        await asyncio.sleep(random.uniform(*SLEEP_RANGE))

                for i in range(iterations):
                    await self.full_swap_task(wallet_name, private_key, proxy)

                    if i != iterations - 1:
                        await asyncio.sleep(random.uniform(*SLEEP_RANGE))

            except BadWalletException:
                msg = f'Incorrect private key, wallet will be skipped'
                self.log_msg(wallet_name=wallet_name, msg=msg, msg_type="critical")

            except Exception as error:
                msg = f'Execution suddenly crashed, error: {error}'
                self.log_msg(wallet_name=wallet_name, msg=msg, msg_type="error")

    async def run_wallets(self):
        semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
        accounts_data = await self.get_accounts_data()

        if SHUFFLE_ACCOUNTS:
            random.shuffle(accounts_data)

        tasks = [
            asyncio.create_task(self.run_wallet(semaphore, False if i < SEMAPHORE_LIMIT else True, *account_data))
            for i, account_data in enumerate(accounts_data)
        ]

        await asyncio.gather(*tasks)
