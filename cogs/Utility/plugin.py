from __future__ import annotations

from .. import Plugin
from typing import Optional, Union
from core import Bot, Embed
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, View
from discord import Interaction, app_commands, Member, User


class Utility(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='ping', description="Shows the bot's latency.")
    async def ping_command(self, ctx):
        embed = Embed(
            description=f"my ping is {round(self.bot.latency * 1000)} ms.")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='avatar', description="Shows the user avatar")
    @app_commands.describe(
        user= "user"
    )
    async def avatar_command(self, ctx: Context, user: Optional[Union[Member, User]]):
        if not user: user = ctx.author
        view= View()
        av_button = Button(label='Download', url=user.display_avatar.url,emoji='⬇️')
        view.add_item(av_button)
        embed = Embed(color=0x303236)
        embed.set_image(url=user.display_avatar)
        embed.set_author(name=f"The avatar of {user.name}:")
        await ctx.send(embed=embed, view=view)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Utility(bot))
