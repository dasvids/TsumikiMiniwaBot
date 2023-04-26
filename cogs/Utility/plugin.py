from __future__ import annotations

from .. import Plugin
from typing import Optional, Union
from core import Bot, Embed
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, View, Select
from discord import Interaction, app_commands, Member, User, SelectOption
from dispie import EmbedCreator

class HelpSelect(Select):
    def __init__(self, bot: commands.AutoShardedBot):
        super().__init__(
            placeholder="Choose a category",
            options= [
                SelectOption(
                    label=cog_name, description= cog.__doc__
                ) for cog_name, cog in bot.cogs.items() if cog.__cog_commands__ and cog_name not in ['Jishaku']
            ]
        )
        self.bot = bot
        
    async def callback(self,interaction: Interaction) -> None:
        cog = self.bot.get_cog(self.values[0])
        assert cog
        
        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)
        
        for i in cog.walk_app_commands():
            commands_mixer.append(i)
            
        embed = Embed(
            title= f"{cog.__cog_name__} Commands",
            description= '\n'.join(
                f"**{command.name}**: `{command.description}`"
                for command in commands_mixer
            )
        )
        await interaction.response.send_message(
            embed = embed,
            ephemeral=True
        )


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
        
    @commands.hybrid_command(name='help', description='Shows list of commands')
    async def help(self, ctx: Context):
        embed = Embed(
            title= "Help command",
            description= "This is help command"
        )
        view = View().add_item(HelpSelect(self.bot))
        await ctx.send(embed=embed,view=view)
        
    @commands.hybrid_command(name='create-embed', description= "Embed builder")
    async def create_embed(self,ctx: Context):
        view = EmbedCreator(bot=self.bot)
        await ctx.send(embed=view.get_default_embed,view=view)
        

async def setup(bot: Bot) -> None:
     await bot.add_cog(Utility(bot))
