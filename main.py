from core.zerion import ZerionClient
from itertools import cycle
from web3 import AsyncWeb3
from core.config import *
from utils.log import log
from utils.file import *
import asyncio
import random


async def zerion_dna_task(client, w3, wallet):
    result = await client.mint_zerion_dna(w3, wallet)
    return result


async def start_work(semaphore, client, w3, private_key):
    async with semaphore:
        await asyncio.sleep(random.randint(*SLEEP_RANGE))
        wallet = w3.eth.account.from_key(private_key)
        result = await zerion_dna_task(client, w3, wallet)

        if result:
            await append_line(private_key, "files/succeeded_wallets.txt")
            return True

        else:
            await append_line(private_key, "files/failed_wallets.txt")
            return False


async def main():
    await clear_file("files/succeeded_wallets.txt")
    await clear_file("files/failed_wallets.txt")

    if USE_PROXY:
        proxies = list(dict.fromkeys(await read_lines("files/proxies.txt")))

        if len(proxies) == 0:
            log.critical("Proxy usage is enabled, but the file with them is empty")
            return
    else:
        log.info("Working without proxies")
        proxies = [None]

    client = ZerionClient()
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    w3_list = [AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(random.choice(NODE_URLS),
                                                     request_kwargs={"proxy": proxy,
                                                                     "timeout": 60})) for proxy in proxies]
    private_keys = list(dict.fromkeys(await read_lines("files/private_keys.txt")))

    if SHUFFLE_ACCOUNTS:
        random.shuffle(private_keys)

    tasks = [asyncio.create_task(start_work(semaphore, client, w3, private_key)) for w3, private_key in
             zip(cycle(w3_list), private_keys)]
    res = await asyncio.gather(*tasks)
    log.info(f'Wallets: {len(res)} Succeeded: {len([x for x in res if x])} Failed: {len([x for x in res if not x])}')


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    except Exception:
        pass

    asyncio.run(main())
