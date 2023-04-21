from math import ceil
import discord
import itertools

def get_print_type(input):
    prate = ""
    card_print = int(input[2:len(input) - 1])
    # very hot if else things for define print
    if card_print > 1000:
        prate = 'hp\xa0'
    elif card_print in range(500, 1000):
        prate = 'hmp'
    elif card_print in range(100, 500):
        prate = 'lmp'
    elif card_print in range(50, 100):
        prate = 'hlp'
    elif card_print in range(10, 50):
        prate = 'llp'
    elif card_print in range(1, 10):
        prate = 'sp\xa0'
    return prate

def get_info(input):
    if int(input["print"][2:len(input["print"]) - 1]) < 100:
        sign = '❔'
    else:
        sign = '✅' if input["is_accepted"] else '❌'

    return f'{input["wl"]} · `{get_print_type(input["print"])}` · {input["ed"]} · {sign}'

class PaginatorView(discord.ui.View):
    current_page: int = 1
    sep: int = 10

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        self.reply = None
        await self.update_message(dict(itertools.islice(self.data.items(), 0, self.sep)))

    def create_embed(self, data: dict):
        embed = discord.Embed(title="dono pricing")
        embed.add_field(name="cards", value='\n'.join([
            f'{key}' for key in data.keys()
        ]), inline=True)
        embed.add_field(name="info", value='\n'.join([
            f'{get_info(data[key])}' for key in data.keys()
        ]), inline=True)
        # embed.add_field(name="rate", value='\n'.join([
        #     f"""`{dict[key]["rate"]}`""" for key in dict.keys()
        # ]))
        embed.add_field(name="prices", value='\n'.join([
            f'`\xa0-\xa0`'
            if get_info(data[key]).split(" · ")[-1] == '❔' else f'{data[key]["price"]}'
            for key in data.keys()
        ]), inline=True)

        total = round(sum([
            float(self.data[key]["price"][1:len(self.data[key]["price"]) - 1]) if
            self.data[key]["is_accepted"] else 0.0 for key in self.data.keys()
        ]))

        embed.description = \
            f'Accepted Total: `{total}` 🎟️\n' \
            f'All Total: `{round(sum([float(self.data[key]["price"][1:len(self.data[key]["price"]) - 1]) for key in self.data.keys()]))}`🎟️'
        embed.set_footer(
            text=f'Showing cards {self.current_page * self.sep - self.sep + 1}-{self.current_page * self.sep} ({len(self.data.keys())} total) - '
                 f'page price: {round(sum([float(data[key]["price"][1:len(data[key]["price"]) - 1]) if data[key]["is_accepted"] else 0.0 for key in data.keys()]))}')
        return embed

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == ceil(len(self.data) / self.sep):
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

        if len(list(filter(lambda x: self.data[x]["is_accepted"], self.data.keys()))) == 0:
            self.get_valid_button.disabled = True
            self.get_valid_button.style = discord.ButtonStyle.gray
        else:
            self.get_valid_button.disabled = False
            self.get_valid_button.style = discord.ButtonStyle.secondary

    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    async def update_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(
            dict(itertools.islice(self.data.items(), from_item, until_item))), view=self
        )

    @discord.ui.button(label='|<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(dict(itertools.islice(self.data.items(), 0, until_item)))

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(dict(itertools.islice(self.data.items(), from_item, until_item)))

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(dict(itertools.islice(self.data.items(), from_item, until_item)))

    @discord.ui.button(label='>|', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = ceil(len(self.data) / self.sep)
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(dict(itertools.islice(self.data.items(), from_item, until_item)))

    @discord.ui.button(emoji='🧀', style=discord.ButtonStyle.primary)
    async def get_valid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        # await self.update_message(dict(itertools.islice(self.data.items(), from_item, until_item)))
        valid_cards = [
            key[1:len(key)-1] if self.data[key]["is_accepted"] else f'' for key in self.data.keys()
        ]
        if self.reply is None:
            self.reply = await self.message.reply(", ".join(list(filter(None, valid_cards))))
        else:
            await self.reply.edit(content=", ".join(list(filter(None, valid_cards))))

