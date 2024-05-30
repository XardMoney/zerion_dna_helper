import asyncio
import functools
import random

from aiohttp import ClientResponseError
from aiohttp.client_exceptions import ClientHttpProxyError, ClientProxyConnectionError
from asyncio.exceptions import TimeoutError
from core.config import (GAS_CONTROL, GWEI_LIMIT, NUMBER_OF_ATTEMPTS, SLEEP_RANGE, SLEEP_RANGE_FOR_GWEI_CHECKS)
from python_socks import ProxyError
from utils.exceptions import CoinGeckoRateLimitException, NoMoreAttemptsException
from utils.networks import Ethereum
from web3 import AsyncHTTPProvider, AsyncWeb3


def check_gas(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if GAS_CONTROL:
            msg = "Starting to check GWEI"
            self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, msg)
            w3 = AsyncWeb3(AsyncHTTPProvider(
                random.choice(Ethereum.rpc), request_kwargs=self.request_kwargs)
            )
            gas = round(AsyncWeb3.from_wei(await w3.eth.gas_price, "gwei"), 3)

            if gas < GWEI_LIMIT:
                msg = "GWEI limit hasn't been exceeded"
                self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, msg,
                             "success")
                return await func(self, *args, **kwargs)

            else:
                time_to_sleep = random.randint(*SLEEP_RANGE_FOR_GWEI_CHECKS)
                msg = f'GWEI limit has been exceeded, will try again in {time_to_sleep} ' \
                      f'{"seconds" if time_to_sleep != 1 else "second"}.'
                self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, msg,
                             "warning")
                await asyncio.sleep(time_to_sleep)

        else:
            return await func(self, *args, **kwargs)

    return wrapper


def retry(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        for _ in range(1, NUMBER_OF_ATTEMPTS + 1):
            try:
                result = await func(self, *args, **kwargs)
                return result

            except (ClientProxyConnectionError, TimeoutError, ClientHttpProxyError, ProxyError, ClientResponseError):
                msg = f'Connection is not stable (proxy: {self.proxy if self.proxy else "None"}), ' \
                      f'will try again in 1 minute'
                self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, msg,
                             "warning")
                await asyncio.sleep(60)

            except CoinGeckoRateLimitException:
                msg = f'CoinGecko API got rate limit, will try again in 5 minutes'
                self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, msg,
                             "warning")
                await asyncio.sleep(300)

            except Exception as error:
                self.log_msg(self.wallet_name, self.network.name, self.__class__.__name__, func.__name__, str(error),
                             "error")
                await asyncio.sleep(random.randint(*SLEEP_RANGE))

        raise NoMoreAttemptsException(f'{func.__name__} failed after {NUMBER_OF_ATTEMPTS} attempts')

    return wrapper
