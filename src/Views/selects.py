from discord import SelectOption, Embed, Colour
from discord.ui import View, select
from src.utils import collection_users
import datetime

class Slots_Option(View):

    @select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Choose the number of days", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maxmimum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            SelectOption(
                label="1 hour (For fast trade)",
                description="Cost: Free",
                emoji='💵',
                value='0'
            ),
            SelectOption(
                label="3 days",
                description="Cost: 60 rbx",
                emoji='💵',
                value='60'
            ),
            SelectOption(
                label="1 week",
                description="Cost: 120 rbx",
                emoji='💵',
                value='120'
            ),
            SelectOption(
                label="1 month",
                description="Cost: 400 rbx",
                emoji='💵',
                value='400'
            ),
        ]
    )
    async def slot_callback(self, select, interaction): # the function called when the user is done selecting options
        for child in self.children:
            child.disabled = True
        key = f'{select.values[0]}-{interaction.user.id}-seller'
        if select.values[0] == '0':           
            collection_users.update_one({'id':str(interaction.user.id)},{'$set':{'token_seller':{'token':key,'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(days=1.0)}, 'payment_seller':{'price':select.values[0],'old': 0, 'new': 0}}})
            await interaction.response.edit_message(view=self)
        else:
            embed = Embed(
                title='Key',
                description=f'Your key is **{key}**, pls introduce it into the game to buy your shop',
                color=Colour.blue()
            )
            embed.add_field(name='Game',value='[link](https://www.roblox.com/games/9906346613/JCommerce)')
            embed.set_footer(text='You just have one day to introduce your "key". Pay in that time, there will be no refunds')
            collection_users.update_one({'id':str(interaction.user.id)},{'$set':{'token_seller':{'token':key,'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(days=1.0)}, 'payment_seller':{'price':select.values[0],'old': 0, 'new': 0}}})
            await interaction.response.edit_message(view=self)
            await interaction.user.send(embed=embed)

class Slots_Upgrade(View):

    @select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Choose the number of days", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maxmimum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            SelectOption(
                label="1 day",
                description="Cost: 25",
                emoji='💵',
                value='25'
            ),
            SelectOption(
                label="3 days",
                description="Cost: 60 rbx",
                emoji='💵',
                value='60'
            ),
            SelectOption(
                label="1 week",
                description="Cost: 120 rbx",
                emoji='💵',
                value='120'
            ),
            SelectOption(
                label="1 month",
                description="Cost: 400 rbx",
                emoji='💵',
                value='400'
            ),
        ]
    )
    async def slot_callback(self, select, interaction): # the function called when the user is done selecting options
        for child in self.children:
            child.disabled = True
        key = f'{select.values[0]}-{interaction.user.id}-seller'
        embed = Embed(
            title='Key',
            description=f'Your key is **{key}**, pls introduce it into the game to buy your shop',
            color=Colour.blue()
        )
        embed.add_field(name='Game',value='[link](https://www.roblox.com/games/9906346613/JCommerce)')
        embed.set_footer(text='You just have one day to introduce your "key". Pay in that time, there will be no refunds')
        collection_users.update_one({'id':str(interaction.user.id)},{'$set':{'token_seller':{'token':key,'created':datetime.datetime.now(),'finish':datetime.datetime.now()+datetime.timedelta(days=1.0)}, 'payment_seller':{'price':select.values[0],'old': 0, 'new': 0}}})
        await interaction.response.edit_message(view=self)
        await interaction.user.send(embed=embed)