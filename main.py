import asyncio

from utils.worker import Worker


async def main():
    worker = Worker()
    await worker.run_wallets()


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    except Exception:
        pass

    asyncio.run(main())
