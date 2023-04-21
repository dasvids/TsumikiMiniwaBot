from __future__ import annotations

from core import Bot
from .. import Plugin


class TestCog(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot):
    await bot.add_cog(TestCog(bot))
