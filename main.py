from __future__ import annotations

import asyncio
import discord
import config
import keep_alive
from core import Bot


async def main():
    discord.utils.setup_logging()
    keep_alive.keep_alive()
    async with Bot() as bot:
        await bot.start(config.TOKEN, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
