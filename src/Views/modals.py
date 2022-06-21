from discord.ui import Modal, InputText
from discord import InputTextStyle, Embed, Colour, PermissionOverwrite
import requests
from src.Views import buttons
from src.utils import collection_users

'''class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Short Input"))
        self.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="Short Input", value=self.children[0].value)
        embed.add_field(name="Long Input", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])'''

BUYER_ROLE_ID = 981616570876969080
GUILD_ID = 976734513000493077
SELLER_ROLE_ID = 977025090313142322


class Create_Embed(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Title", style=InputTextStyle.short))
        self.add_item(InputText(label="Description", style=InputTextStyle.long))
        self.add_item(InputText(label="Reaction", style=InputTextStyle.short, required=False))

    async def callback(self, interaction):
        embed = Embed(title=self.children[0].value, description=self.children[1].value, color=Colour.blue())
        message = await interaction.channel.send(embed=embed)
        if self.children[2].value:
            await message.add_reaction(self.children[2].value)
        await interaction.response.send_message('You have created a embed', ephemeral=True)

#------------------------- VERIFY ------------------------------------------------
class Verify_Modal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.add_item(InputText(label='Enter your User ID (Roblox)',style=InputTextStyle.short))

    async def callback(self, interaction):
        roblox_id = self.children[0].value
        roblox_user = requests.get(f'https://users.roblox.com/v1/users/{roblox_id}')
        if roblox_user.status_code == 200:
            response = requests.get(f'https://thumbnails.roblox.com/v1/users/avatar?userIds={roblox_id}&size=250x250&format=Png&isCircular=false')
            embed = Embed(
                title='Roblox verify',
                description=f'Is **{roblox_user.json()["name"]}** your Roblox User?',
                color=Colour.blue()
            )
            embed.set_image(url=response.json()['data'][0]['imageUrl'])
            embed.set_footer(text='This information is necessary for the to\nuse our MM system',icon_url='')
            await interaction.response.send_message(f'{interaction.user.mention}, check your dm',delete_after=3.0, ephemeral=True)
            await interaction.user.send(embed=embed,view=buttons.Verify(roblox_id=roblox_id))
        else:
            await interaction.response.send_message(f'{interaction.user.mention}, the User ID does not exist',delete_after=3.0, ephemeral=True)
    
class Verify_Place(Modal):
    def __init__(self, roblox_id, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.roblox_id = roblox_id

        self.add_item(InputText(label='Enter your Place ID',style=InputTextStyle.short))

    async def callback(self,interaction):
        exist_id = requests.get(f'https://api.roblox.com/universes/get-universe-containing-place?placeid={self.children[0].value}')
        if exist_id.status_code == 200:
            universe_id = exist_id.json()['UniverseId']
            response = requests.get(f"https://games.roblox.com/v1/games", params=f"universeIds={universe_id}", headers={'Content-Type': 'application/json'})
            creator_id = response.json()['data'][0]['creator']['id']
            if str(self.roblox_id) == str(creator_id):
                collection_users.update_one({'id':str(interaction.user.id)},{'$set':{'roblox_id':str(self.roblox_id), 'universe_id':str(universe_id)}})
                await interaction.response.send_message(f'{interaction.user.mention}, your data has been saved correctly, now you can use our MM system', delete_after=3.0, ephemeral=True)
            else:
                await interaction.response.send_message(f'{interaction.user.mention}, the roblox user does not match with the place', delete_after=3.0, ephemeral=True)
        else:
            await interaction.response.send_message(f'{interaction.user.mention}, there was a mistake, try it again', delete_after=3.0, ephemeral=True)

#---------------------------------------------EDIT CHANNEL NAME---------------------------------------------------

class Change_Name(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.add_item(InputText(label='Introduce the Name', style=InputTextStyle.short))

    async def callback(self, interaction):
        user = collection_users.find_one({'id':str(interaction.user.id)})
        channel = user['shop']['channel']
        guild = interaction.guild
        CATEGORY_SHOP_ID = 983845624841654332
        shop_category = guild.get_channel(CATEGORY_SHOP_ID)
        buyer_role = guild.get_role(BUYER_ROLE_ID)
        permissions = PermissionOverwrite()
        permissions.send_messages = False
        permissions.read_messages = True
        permissions.read_message_history = True
        name_channel = self.children[0].value
        if channel['id']:
            channel_user = await guild.fetch_channel(channel['id'])
            await channel_user.edit(name=name_channel)
            embed = Embed(
                    title='Shop',
                    description=f'The name of your channel has been changed to **{name_channel}**',
                    color=Colour.blue()
                )
            await interaction.user.send(embed=embed)
        else:
            channel_user = await shop_category.create_text_channel(name = name_channel, overwrites={buyer_role:permissions})
            collection_users.update_one({'id':str(interaction.user.id)},{'$set':{'shop.channel.id':channel_user.id}})
            embed = Embed(
                title='Shop',
                description=f'Your channel has been created with the name **{name_channel}**',
                color=Colour.blue()
            )
            embed.set_footer(text='You can change the channel name one time every 15 min using "/shop edit name"')
            await interaction.user.send(embed=embed)
        await interaction.response.send_message(f'{interaction.user.mention}, check your dm', delete_after=3.0, ephemeral=True)


# --------------------------------------------------- Edit messages -------------------------------------------------------------------

class Slot(Modal):
    def __init__(self, slot, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.slot = slot
        self.add_item(InputText(label='Introduce the Title', style=InputTextStyle.short, placeholder='Example: "GFX" or "Piece Game Fruits Shop"'))
        self.add_item(InputText(label='Introduce the Description', style=InputTextStyle.paragraph, placeholder='Example:\nGFX One Person - 50 rbx'))
        self.add_item(InputText(label='Introduce your portfolio (Option)', style=InputTextStyle.short, required=False, placeholder='Example: https://devforum.roblox.com/porfolio'))
        self.add_item(InputText(label='Introduce a note (Option)', style=InputTextStyle.short, required=False))
        self.add_item(InputText(label='Introduce the image link (Option)', style=InputTextStyle.short, required=False, placeholder='Example: https://gyazo.com/example'))

    async def callback(self, interaction):
        user = collection_users.find_one({'id':str(interaction.user.id)})
        channel = user['shop']['channel']
        guild = interaction.guild
        channel_user = await guild.fetch_channel(channel['id'])
        #Variables message
        title = self.children[0].value
        description = self.children[1].value
        portfolio = self.children[2].value
        note = self.children[3].value
        image = self.children[4].value

        embed = Embed(
            title=title,
            description=description,
            color=Colour.blue()
        )
        if portfolio:
            embed.add_field(name='Portfolio', value=f'[link]({portfolio})', inline=False)
        if note:
            embed.add_field(name='Note', value=note, inline=False)
        embed.add_field(name='Discord', value=interaction.user.mention)
        if image:
            embed.set_image(url=image)
        if not channel['id']:
            await interaction.response.send_message(f'{interaction.user.mention}, you must create your channel using "/shop edit name"', delete_after=3.0, ephemeral=True)
        else:
            if not channel['messages'][int(self.slot)]:
                try:
                    message = await channel_user.send(embed=embed, view=buttons.Button_Buy())
                    collection_users.update_one({'id':str(interaction.user.id)},{'$set':{f'shop.channel.messages.{int(self.slot)}':message.id}})
                    await interaction.response.send_message(f'{interaction.user.mention}, your message has been successfully saved/modified"', delete_after=3.0, ephemeral=True)
                except:
                    await interaction.response.send_message(f'{interaction.user.mention}, your image must be a link (http or https)', delete_after=3.0, ephemeral=True)
            else:
                message = await channel_user.fetch_message(channel['messages'][int(self.slot)])
                try:
                    await message.edit(embed=embed, view=buttons.Button_Buy())
                    await interaction.response.send_message(f'{interaction.user.mention}, your message has been successfully saved/modified"', delete_after=3.0, ephemeral=True)
                except:
                    await interaction.response.send_message(f'{interaction.user.mention}, your image must be a link (http or https)', delete_after=3.0, ephemeral=True)

