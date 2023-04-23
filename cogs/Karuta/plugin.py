from __future__ import annotations
import asyncio
import re

from .. import Plugin
from core.embed import Embed
from database.mongo import rates_db
from core import Bot
from ..Utility.paginator import PaginatorView
import discord
from discord import Interaction, app_commands, Message
from discord.ext import commands

def my_regex_search(row):
    return re.search(r'(`♡\d{1,5}\xa0{0,4}`)\s·\s\*\*(`\xa0{0,4}[0-9a-z]{1,7}`)\*\*\s·\s(`[★☆]{4}`)\s·\s'
                     r'(`#\d{1,5}\xa0{0,5}`)\s·\s(`◈\d`)\s·\s'
                     r'~?~?((\s?[\w#()/&\'*!.,%~;?:-]+)+)\s·\s\*\*((\s?[\w#()/&!\'.,*;?~%:-]+)+)\*\*~?~?',
                     row)
    
def remove_apos(row):
    return row[2:len(row) - 1]

def get_print_type(card_print):
    if card_print > 1000:
        prate = 'hp'
    elif card_print in range(500, 1000):
        prate = 'hmp'
    elif card_print in range(100, 500):
        prate = 'lmp'
    elif card_print in range(50, 100):
        prate = 'hlp'
    elif card_print in range(10, 50):
        prate = 'llp'
    elif card_print in range(1, 10):
        prate = 'sp'
    return prate

def get_list_info(mlist):
    MatchesList = [my_regex_search(x) for x in mlist]
    ed = {}
    for edition in rates_db.find({},{'_id': 0}):
        subed = {}
        for t in edition.keys():
            subed.update({t : edition[t]})
            
        ed.update({
            int(edition['edition']): subed})

    cardsinfo = []

    for match in MatchesList:
        card_print = int(remove_apos(match.group(4)))
        wl = int(remove_apos(match.group(1)))
        edition = int(remove_apos(match.group(5)))
        print_type = get_print_type(card_print)
        price = wl / \
            ed[edition][print_type] if ed[edition][print_type] != 0 else 0
        # prices.append(price)
        cardsinfo.append({
            match.group(2): {
                "wl": match.group(1),
                "print": match.group(4),
                "ed": match.group(5),
                "series": match.group(6),
                "character": match.group(8),
                "price": f"""`{round(price, 2)}`""",
                "is_accepted": True if price >= 3 else False
            }
        })

    return cardsinfo


class Karuta(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="change",
        help="help",
        description="sets rate to edition and for following rate print",
        brief="sets rate",
        usage="change <ed> <print definition(hp for example)> <value: int>"
    )
    @app_commands.describe(
        edition="Karuta card edition (ex: 5)",
        kprint="print type (ex: hp)",
        value="rate value (ex: 180)"
    )
    @commands.has_permissions(administrator=True)
    async def change(self, ctx: commands.Context, edition, kprint, value: int):
        if rates_db.find_one({'edition': edition}) is None:
            tmp_ed = {
                "edition": edition,
                "sp": 0,
                "llp": 0,
                "hlp": 0,
                "lmp": 0,
                "hmp": 0,
                "hp": 0
            }

            rates_db.insert_one(tmp_ed)

        rates_db.update_one({"edition": edition},
                            {"$set": {kprint: value}})
        embed = Embed()
        embed.description = f'you successfully set `{value}` rate for ed{edition} {kprint}'
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="kv",
        help="karuta view",
        description="view rates of karuta things",
        brief="view rate",
        usage="kv <ed>"
    )
    @app_commands.describe(
        ed="Karuta card edition (ex: 5)",
        kprint="print type (ex: hp)"
    )
    async def kv(self, ctx, ed, kprint=None):
        embed = Embed()
        if rates_db.find_one({'edition': ed}) is None:
            embed.title = f'Something went wrong'
            embed.description = f'cant find rate for {ed} {kprint}'
        else:
            if kprint is not None:
                founded = rates_db.find_one(
                    {'edition': ed}, {'_id': 0, 'edition': 0})[kprint]
                embed.title = f'Showing rates for ed{ed} {kprint}'
                embed.add_field(name=kprint, value=founded)
            else:
                founded = rates_db.find_one(
                    {'edition': ed}, {'_id': 0, 'edition': 0})
                embed.title = f'Showing rates for ed{ed}'
                for key in founded.keys():
                    embed.add_field(name=key, value=founded[key])

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if re.search(r'(o\s+(is)|[:=]\s*wl?)|(wl?(<>|>>|<<|<=?\d+|>=?d+))', message.content):
            try:
                karuta_msg = await self.bot.wait_for(
                    "message",
                    check=lambda msg: msg.reference.message_id == message.id and 
                    msg.author.id == 646937666251915264,
                    #str.startswith(msg.embeds[0].description.split('\n')[2],f"The list is empty."),
                    timeout=30
                )

                await karuta_msg.add_reaction('🎟️')

                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user:
                    reaction.emoji == '🎟️' and
                    user.id == message.author.id and
                    re.search(
                        "Cards carried by", reaction.message.embeds[0].description.split('\n')[0]),
                    timeout=30
                )
            except asyncio.TimeoutError:
                return

            cards = {}
            
            for elem in get_list_info(reaction.message.embeds[0].description.split('\n')[2:]):
                cards.update(elem)

            pagination_view = PaginatorView()
            pagination_view.data = cards
            await pagination_view.send(reaction.message.channel)

            while True:
                try:
                    # waiting when user go to next page of karuta
                    new_karuta_msg = await self.bot.wait_for(
                        "message_edit",
                        check=lambda before, after:
                        after.author.id == 646937666251915264 and after.id == karuta_msg.id,
                        timeout=None
                    )
                    for elem in get_list_info(new_karuta_msg[1].embeds[0].description.split('\n')[2:]):
                        cards.update(elem)

                    pagination_view.data = cards

                    # to update total price
                    await pagination_view.update_data()

                except asyncio.TimeoutError:
                    return


async def setup(bot: Bot) -> None:
    await bot.add_cog(Karuta(bot))
