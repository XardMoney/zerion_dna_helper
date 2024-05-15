from core.config import SLEEP_RANGE, SEMAPHORE_LIMIT
from utils.file import append_line, clear_file
from settings import USE_PROXY, SHUFFLE_ACCOUNTS, ENCRYPT_FILES
from core.zerion import ZerionClient
from itertools import cycle
from utils.log import log
import asyncio
import random

from utils.prepare import get_data


async def start_work(semaphore, client, sleep_needed):
    async with semaphore:
        if sleep_needed:
            sleep_time = random.randint(*SLEEP_RANGE)
            log.info(f'Sleeping: {sleep_time} second')
            await asyncio.sleep(sleep_time)

        result = await client.mint_zerion_dna()

        if result:
            await append_line(client.wallet.address, "files/succeeded_wallets.txt")
            return True

        else:
            await append_line(client.wallet.address, "files/failed_wallets.txt")
            return False


async def main():
    await clear_file("files/succeeded_wallets.txt")
    await clear_file("files/failed_wallets.txt")
    if USE_PROXY:
        proxies = get_data("files/proxies.txt", encrypted=ENCRYPT_FILES)
        if len(proxies) == 0:
            log.critical("Proxy usage is enabled, but the file with them is empty")
            return
    else:
        log.info("Working without proxies")
        proxies = [None]

    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    private_keys = get_data("files/private_keys.txt", encrypted=ENCRYPT_FILES)

    wallets_with_proxies = list(zip(cycle(proxies), private_keys))

    if SHUFFLE_ACCOUNTS:
        random.shuffle(wallets_with_proxies)

    tasks = []
    for i, (proxy, private_key) in enumerate(wallets_with_proxies):
        client = ZerionClient('ethereum', private_key, proxy)
        tasks.append(
            asyncio.create_task(
                start_work(
                    semaphore, client, sleep_needed=False if i < SEMAPHORE_LIMIT else True
                )
            )
        )

    res = await asyncio.gather(*tasks)
    log.info(f'Wallets: {len(res)} Succeeded: {len([x for x in res if x])} Failed: {len([x for x in res if not x])}')


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    except Exception:
        pass

    asyncio.run(main())
