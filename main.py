from __future__ import annotations

import asyncio
import discord
import config
from core import Bot


async def main():
    discord.utils.setup_logging()
    async with Bot() as bot:
        await bot.start(config.TOKEN, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
